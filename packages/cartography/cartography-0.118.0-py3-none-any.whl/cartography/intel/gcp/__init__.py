import json
import logging
from collections import namedtuple
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import neo4j
from google.auth.credentials import Credentials as GoogleCredentials
from googleapiclient.discovery import HttpError
from googleapiclient.discovery import Resource

from cartography.config import Config
from cartography.graph.job import GraphJob
from cartography.intel.gcp import compute
from cartography.intel.gcp import dns
from cartography.intel.gcp import gke
from cartography.intel.gcp import iam
from cartography.intel.gcp import storage
from cartography.intel.gcp.clients import build_client
from cartography.intel.gcp.crm.folders import sync_gcp_folders
from cartography.intel.gcp.crm.orgs import sync_gcp_organizations
from cartography.intel.gcp.crm.projects import sync_gcp_projects
from cartography.models.gcp.crm.folders import GCPFolderSchema
from cartography.models.gcp.crm.organizations import GCPOrganizationSchema
from cartography.models.gcp.crm.projects import GCPProjectSchema
from cartography.util import run_analysis_job
from cartography.util import timeit

logger = logging.getLogger(__name__)

# Mapping of service short names to their full names as in docs. See https://developers.google.com/apis-explorer,
# and https://cloud.google.com/service-usage/docs/reference/rest/v1/services#ServiceConfig
Services = namedtuple("Services", "compute storage gke dns iam")
service_names = Services(
    compute="compute.googleapis.com",
    storage="storage.googleapis.com",
    gke="container.googleapis.com",
    dns="dns.googleapis.com",
    iam="iam.googleapis.com",
)


def _services_enabled_on_project(serviceusage: Resource, project_id: str) -> Set:
    """
    Return a list of all Google API services that are enabled on the given project ID.
    See https://cloud.google.com/service-usage/docs/reference/rest/v1/services/list for data shape.
    :param serviceusage: the serviceusage resource provider. See https://cloud.google.com/service-usage/docs/overview.
    :param project_id: The project ID number to sync.  See  the `projectId` field in
    https://cloud.google.com/resource-manager/reference/rest/v1/projects
    :return: A set of services that are enabled on the project
    """
    try:
        req = serviceusage.services().list(
            parent=f"projects/{project_id}",
            filter="state:ENABLED",
        )
        services = set()
        while req is not None:
            res = req.execute()
            if "services" in res:
                services.update({svc["config"]["name"] for svc in res["services"]})
            req = serviceusage.services().list_next(
                previous_request=req,
                previous_response=res,
            )
        return services
    except HttpError as http_error:
        http_error = json.loads(http_error.content.decode("utf-8"))
        # This is set to log-level `info` because Google creates many projects under the hood that cartography cannot
        # audit (e.g. adding a script to a Google spreadsheet causes a project to get created) and we don't need to emit
        # a warning for these projects.
        logger.info(
            f"HttpError when trying to get enabled services on project {project_id}. "
            f"Code: {http_error['error']['code']}, Message: {http_error['error']['message']}. "
            f"Skipping.",
        )
        return set()


def _sync_project_resources(
    neo4j_session: neo4j.Session,
    projects: List[Dict],
    gcp_update_tag: int,
    common_job_parameters: Dict,
    credentials: Optional[GoogleCredentials] = None,
) -> None:
    """
    Syncs GCP service-specific resources (Compute, Storage, GKE, DNS, IAM) for each project.
    :param neo4j_session: The Neo4j session
    :param projects: A list of projects containing at minimum a "projectId" field.
    :param gcp_update_tag: The timestamp value to set our new Neo4j nodes with
    :param common_job_parameters: Other parameters sent to Neo4j
    :return: Nothing
    """
    logger.info("Syncing resources for %d GCP projects.", len(projects))
    # Per-project sync across services
    for project in projects:
        project_id = project["projectId"]
        common_job_parameters["PROJECT_ID"] = project_id
        enabled_services = _services_enabled_on_project(
            build_client("serviceusage", "v1", credentials=credentials),
            project_id,
        )

        if service_names.compute in enabled_services:
            logger.info("Syncing GCP project %s for Compute.", project_id)
            compute_cred = build_client("compute", "v1", credentials=credentials)
            compute.sync(
                neo4j_session,
                compute_cred,
                project_id,
                gcp_update_tag,
                common_job_parameters,
            )

        if service_names.storage in enabled_services:
            logger.info("Syncing GCP project %s for Storage.", project_id)
            storage_cred = build_client("storage", "v1", credentials=credentials)
            storage.sync_gcp_buckets(
                neo4j_session,
                storage_cred,
                project_id,
                gcp_update_tag,
                common_job_parameters,
            )

        if service_names.gke in enabled_services:
            logger.info("Syncing GCP project %s for GKE.", project_id)
            container_cred = build_client("container", "v1", credentials=credentials)
            gke.sync_gke_clusters(
                neo4j_session,
                container_cred,
                project_id,
                gcp_update_tag,
                common_job_parameters,
            )

        if service_names.dns in enabled_services:
            logger.info("Syncing GCP project %s for DNS.", project_id)
            dns_cred = build_client("dns", "v1", credentials=credentials)
            dns.sync(
                neo4j_session,
                dns_cred,
                project_id,
                gcp_update_tag,
                common_job_parameters,
            )

        if service_names.iam in enabled_services:
            logger.info("Syncing GCP project %s for IAM.", project_id)
            iam_cred = build_client("iam", "v1", credentials=credentials)
            iam.sync(
                neo4j_session,
                iam_cred,
                project_id,
                gcp_update_tag,
                common_job_parameters,
            )

        del common_job_parameters["PROJECT_ID"]


@timeit
def start_gcp_ingestion(
    neo4j_session: neo4j.Session,
    config: Config,
    credentials: Optional[GoogleCredentials] = None,
) -> None:
    """
    Starts the GCP ingestion process by initializing Google Application Default Credentials, creating the necessary
    resource objects, listing all GCP organizations and projects available to the GCP identity, and supplying that
    context to all intel modules.
    :param neo4j_session: The Neo4j session
    :param config: A `cartography.config` object
    :return: Nothing
    """
    common_job_parameters = {
        "UPDATE_TAG": config.update_tag,
    }

    # IMPORTANT: We defer cleanup for hierarchical resources (orgs, folders, projects) and run them
    # in reverse order. This prevents orphaned nodes when a parent is deleted.
    # Without this, deleting an org would break its relationships to projects/folders, leaving them
    # disconnected and unable to be cleaned up by their own cleanup jobs.
    #
    # Order of operations:
    # 1. Sync all orgs
    # 2. For each org:
    #    a. Sync folders and projects
    #    b. Sync project resources (with immediate cleanup)
    #    c. Clean up projects and folders for this org
    # 3. Clean up all orgs at the end
    #
    # This ensures children are cleaned up before their parents.

    orgs = sync_gcp_organizations(
        neo4j_session,
        config.update_tag,
        common_job_parameters,
        credentials=credentials,
    )

    # Track org cleanup jobs to run at the very end
    org_cleanup_jobs = []

    # For each org, sync its folders and projects (as sub-resources), then ingest per-project services
    for org in orgs:
        org_resource_name = org.get("name", "")  # e.g., organizations/123456789012
        if not org_resource_name or "/" not in org_resource_name:
            logger.error(f"Invalid org resource name: {org_resource_name}")
            continue

        # Store the full resource name for cleanup operations
        common_job_parameters["ORG_RESOURCE_NAME"] = org_resource_name

        # Sync folders under org
        folders = sync_gcp_folders(
            neo4j_session,
            config.update_tag,
            common_job_parameters,
            org_resource_name,
            credentials=credentials,
        )

        # Sync projects under org and each folder
        projects = sync_gcp_projects(
            neo4j_session,
            org_resource_name,
            folders,
            config.update_tag,
            common_job_parameters,
            credentials=credentials,
        )

        # Ingest per-project resources (these run their own cleanup immediately since they're leaf nodes)
        _sync_project_resources(
            neo4j_session,
            projects,
            config.update_tag,
            common_job_parameters,
            credentials=credentials,
        )

        # Clean up projects and folders for this org (children before parents)
        logger.debug(f"Running cleanup for projects and folders in {org_resource_name}")
        GraphJob.from_node_schema(GCPProjectSchema(), common_job_parameters).run(
            neo4j_session
        )
        GraphJob.from_node_schema(GCPFolderSchema(), common_job_parameters).run(
            neo4j_session
        )

        # Save org cleanup job for later
        org_cleanup_jobs.append((GCPOrganizationSchema, dict(common_job_parameters)))

        # Remove org ID from common job parameters after processing
        del common_job_parameters["ORG_RESOURCE_NAME"]

    # Run all org cleanup jobs at the very end, after all children have been cleaned up
    logger.info("Running cleanup for GCP organizations")
    for schema_class, params in org_cleanup_jobs:
        GraphJob.from_node_schema(schema_class(), params).run(neo4j_session)

    run_analysis_job(
        "gcp_compute_asset_inet_exposure.json",
        neo4j_session,
        common_job_parameters,
    )

    run_analysis_job(
        "gcp_gke_asset_exposure.json",
        neo4j_session,
        common_job_parameters,
    )

    run_analysis_job(
        "gcp_gke_basic_auth.json",
        neo4j_session,
        common_job_parameters,
    )
