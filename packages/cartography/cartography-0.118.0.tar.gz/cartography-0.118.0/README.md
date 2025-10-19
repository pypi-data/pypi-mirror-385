![Cartography](docs/root/images/logo-horizontal.png)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/cartography-cncf/cartography/badge)](https://scorecard.dev/viewer/?uri=github.com/cartography-cncf/cartography)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/9637/badge)](https://www.bestpractices.dev/projects/9637)
![build](https://github.com/cartography-cncf/cartography/actions/workflows/publish-to-ghcr-and-pypi.yml/badge.svg)



Cartography is a Python tool that consolidates infrastructure assets and the relationships between them in an intuitive graph view powered by a [Neo4j](https://www.neo4j.com) database.

![Visualization of RDS nodes and AWS nodes](docs/root/images/accountsandrds.png)

## Why Cartography?
Cartography aims to enable a broad set of exploration and automation scenarios. It is particularly good at exposing otherwise hidden dependency relationships between your service's assets so that you may validate assumptions about security risks.

Service owners can generate asset reports, Red Teamers can discover attack paths, and Blue Teamers can identify areas for security improvement. All can benefit from using the graph for manual exploration through a web frontend interface, or in an automated fashion by calling the APIs.

Cartography is not the only [security](https://github.com/dowjones/hammer) [graph](https://github.com/BloodHoundAD/BloodHound) [tool](https://github.com/Netflix/security_monkey) [out](https://github.com/vysecurity/ANGRYPUPPY) [there](https://github.com/duo-labs/cloudmapper), but it differentiates itself by being fully-featured yet generic and [extensible](https://cartography-cncf.github.io/cartography/dev/writing-analysis-jobs.html) enough to help make anyone better understand their risk exposure, regardless of what platforms they use. Rather than being focused on one core scenario or attack vector like the other linked tools, Cartography focuses on flexibility and exploration.

You can learn more about the story behind Cartography in our [presentation at BSidesSF 2019](https://www.youtube.com/watch?v=ZukUmZSKSek).


## Supported platforms
- [Airbyte](https://cartography-cncf.github.io/cartography/modules/airbyte/index.html) - Organization, Workspace, User, Source, Destination, Connection, Tag, Stream
- [Amazon Web Services](https://cartography-cncf.github.io/cartography/modules/aws/index.html) - ACM, API Gateway, CloudWatch, CodeBuild, Config, Cognito, EC2, ECS, ECR (including multi-arch images, image layers, and attestations), EFS, Elasticsearch, Elastic Kubernetes Service (EKS), DynamoDB, Glue,  GuardDuty, IAM, Inspector, KMS, Lambda, RDS, Redshift, Route53, S3, Secrets Manager(Secret Versions), Security Hub, SNS, SQS, SSM, STS, Tags
- [Anthropic](https://cartography-cncf.github.io/cartography/modules/anthropic/index.html) - Organization, ApiKey, User, Workspace
- [BigFix](https://cartography-cncf.github.io/cartography/modules/bigfix/index.html) - Computers
- [Cloudflare](https://cartography-cncf.github.io/cartography/modules/cloudflare/index.html) - Account, Role, Member, Zone, DNSRecord
- [Crowdstrike Falcon](https://cartography-cncf.github.io/cartography/modules/crowdstrike/index.html) - Hosts, Spotlight vulnerabilities, CVEs
- [DigitalOcean](https://cartography-cncf.github.io/cartography/modules/digitalocean/index.html)
- [Duo](https://cartography-cncf.github.io/cartography/modules/duo/index.html) - Users, Groups, Endpoints
- [GitHub](https://cartography-cncf.github.io/cartography/modules/github/index.html) - repos, branches, users, teams, dependency graph manifests, dependencies
- [Google Cloud Platform](https://cartography-cncf.github.io/cartography/modules/gcp/index.html) - Cloud Resource Manager, Compute, DNS, Storage, Google Kubernetes Engine
- [Google GSuite](https://cartography-cncf.github.io/cartography/modules/gsuite/index.html) - users, groups
- [Kandji](https://cartography-cncf.github.io/cartography/modules/kandji/index.html) - Devices
- [Keycloak](https://cartography-cncf.github.io/cartography/modules/keycloak/index.html) - Realms, Users, Groups, Roles, Scopes, Clients, IdentityProviders, Authentication Flows, Authentication Executions, Organizations, Organization Domains
- [Kubernetes](https://cartography-cncf.github.io/cartography/modules/kubernetes/index.html) - Cluster, Namespace, Service, Pod, Container, ServiceAccount, Role, RoleBinding, ClusterRole, ClusterRoleBinding, OIDCProvider
- [Lastpass](https://cartography-cncf.github.io/cartography/modules/lastpass/index.html) - users
- [Microsoft Azure](https://cartography-cncf.github.io/cartography/modules/azure/index.html) - App Service, Container Instance, CosmosDB, Functions, Logic Apps, Resource Group, SQL, Storage, Virtual Machine
- [Microsoft Entra ID](https://cartography-cncf.github.io/cartography/modules/entra/index.html) -  Users, Groups, Applications, OUs, App Roles, federation to AWS Identity Center
- [NIST CVE](https://cartography-cncf.github.io/cartography/modules/cve/index.html) - Common Vulnerabilities and Exposures (CVE) data from NIST database
- [Okta](https://cartography-cncf.github.io/cartography/modules/okta/index.html) - users, groups, organizations, roles, applications, factors, trusted origins, reply URIs, federation to AWS roles, federation to AWS Identity Center
- [OpenAI](https://cartography-cncf.github.io/cartography/modules/openai/index.html) - Organization, AdminApiKey, User, Project, ServiceAccount, ApiKey
- [Oracle Cloud Infrastructure](https://cartography-cncf.github.io/cartography/modules/oci/index.html) - IAM
- [PagerDuty](https://cartography-cncf.github.io/cartography/modules/pagerduty/index.html) - Users, teams, services, schedules, escalation policies, integrations, vendors
- [Scaleway](https://cartography-cncf.github.io/cartography/modules/scaleway/index.html) - Projects, IAM, Local Storage, Instances
- [SentinelOne](https://cartography-cncf.github.io/cartography/modules/sentinelone/index.html) - Accounts, Agents
- [SnipeIT](https://cartography-cncf.github.io/cartography/modules/snipeit/index.html) - Users, Assets
- [Tailscale](https://cartography-cncf.github.io/cartography/modules/tailscale/index.html) - Tailnet, Users, Devices, Groups, Tags, PostureIntegrations
- [Trivy Scanner](https://cartography-cncf.github.io/cartography/modules/trivy/index.html) - AWS ECR Images


## Philosophy
Here are some points that can help you decide if adopting Cartography is a good fit for your problem.

### What Cartography is
- A simple Python script that pulls data from multiple providers and writes it to a Neo4j graph database in batches.
- A powerful analysis tool that captures the current snapshot of the environment, building a uniquely useful inventory where you can ask complex questions such as:
  - Which identities have access to which datastores?
  - What are the cross-tenant permission relationships in the environment?
  - What are the network paths in and out of the environment?
  - What are the backup policies for my datastores?
- Battle-tested in production by [many companies](#who-uses-cartography).
- Straightforward to extend with your own custom plugins.
- Provides a useful data-plane that you can build automation and CSPM (Cloud Security Posture Management) applications on top of.

### What Cartography is not
- A near-real time capability.
  - Cartography is not designed for very fast updates. Cartography writes to the database in a batches (not streamed).
  - Cartography is also limited by how most upstream sources only provide APIs to retrieve assets in a batched manner.
- By itself, Cartography does not capture data changes over time.
  - Although we do include a [drift detection](https://cartography-cncf.github.io/cartography/usage/drift-detect.html) feature.
  - It's also possible to implement other processes in your Cartography installation to make this happen.


## Install and configure

### Trying out Cartography on a test machine
Start [here](https://cartography-cncf.github.io/cartography/install.html) to set up a test graph and get data into it.

### Setting up Cartography in production
When you are ready to try it in production, read [here](https://cartography-cncf.github.io/cartography/ops.html) for recommendations on getting cartography spun up in your environment.

## Usage

### Running rules

You can check your environment against common security frameworks using the `cartography-rules` command.

```bash
cartography-rules run all
```

See [the rules docs](https://cartography-cncf.github.io/cartography/usage/rules.html) for more detail.


### Querying the database directly

![poweruser.png](docs/root/images/poweruser.png)

Now that data is in the graph, you can quickly start with our [querying tutorial](https://cartography-cncf.github.io/cartography/usage/tutorial.html). Our [data schema](https://cartography-cncf.github.io/cartography/usage/schema.html) is a helpful reference when you get stuck.

### Building applications around Cartography
Directly querying Neo4j is already very useful as a sort of "swiss army knife" for security data problems, but you can also build applications and data pipelines around Cartography. View this doc on [applications](https://cartography-cncf.github.io/cartography/usage/applications.html).


## Docs

See [here](https://cartography-cncf.github.io/cartography/)

## Community

- Hang out with us on Slack: Join the CNCF Slack workspace [here](https://communityinviter.com/apps/cloud-native/cncf), and then join the `#cartography` channel.
- Talk to us and see what we're working on at our [monthly community meeting](https://zoom-lfx.platform.linuxfoundation.org/meetings/cartography?view=week).
  - Meeting minutes are [here](https://docs.google.com/document/d/1VyRKmB0dpX185I15BmNJZpfAJ_Ooobwz0U1WIhjDxvw).
  - Recorded videos from before 2025 are posted [here](https://www.youtube.com/playlist?list=PLMga2YJvAGzidUWJB_fnG7EHI4wsDDsE1).

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

## Contributing
Thank you for considering contributing to Cartography!

### Code of conduct
All contributors and participants of this project must follow the [CNCF code of conduct](https://github.com/cncf/foundation/blob/main/code-of-conduct.md).

### Bug reports and feature requests and discussions
Submit a GitHub issue to report a bug or request a new feature. If we decide that the issue needs more discussion - usually because the scope is too large or we need to make careful decision - we will convert the issue to a [GitHub Discussion](https://github.com/cartography-cncf/cartography/discussions).

### Developing Cartography

Get started with our [developer documentation](https://cartography-cncf.github.io/cartography/dev/developer-guide.html). Please feel free to submit your own PRs to update documentation if you've found a better way to explain something.

## Who uses Cartography?

1. [Lyft](https://www.lyft.com)
1. [Thought Machine](https://thoughtmachine.net/)
1. [MessageBird](https://messagebird.com)
1. [Cloudanix](https://www.cloudanix.com/)
1. [Corelight](https://www.corelight.com/)
1. [SubImage](https://subimage.io)
1. {Your company here} :-)

If your organization uses Cartography, please file a PR and update this list. Say hi on Slack too!

---

Cartography is a [Cloud Native Computing Foundation](https://www.cncf.io/) sandbox project.<br>
<div style="background-color: white; display: inline-block; padding: 10px;">
  <img src="docs/root/images/cncf-color.png" alt="CNCF Logo" width="200">
</div>
