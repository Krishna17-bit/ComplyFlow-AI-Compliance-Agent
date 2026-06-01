# AcmeCloud Security Policy

Owner: Security Lead  
Review cadence: Quarterly  
Last reviewed: 2026-04-15

## Governance and scope
AcmeCloud maintains an information security program covering production systems, customer data, employee devices, cloud infrastructure, application code, and vendor-managed services. Security responsibilities are assigned to executive leadership, engineering, operations, and support teams. Policy exceptions require approval from the Security Lead and are reviewed during the quarterly security review.

## Access control
Administrative access requires single sign-on and multi-factor authentication. Production access follows least privilege and role-based access. Access requests must include business justification and manager approval. Access rights are reviewed quarterly for production systems, cloud consoles, source code repositories, and support tools. Leavers are removed from production and corporate systems within one business day after HR notification.

## Password and authentication
Employees must use the company password manager. Password reuse is prohibited. MFA is required for email, cloud infrastructure, source code repositories, and administrative SaaS applications. Shared accounts are not allowed unless documented as a break-glass account with restricted access and review.

## Encryption
Customer data is encrypted in transit using TLS 1.2 or higher. Production databases and object storage use encryption at rest. Encryption keys are managed through the cloud provider key management service. Access to key administration is restricted to approved infrastructure administrators.

## Logging and monitoring
Production systems generate application, infrastructure, access, and security logs. Logs are retained for at least 180 days. Alerts are routed to the operations channel and reviewed during business hours. Critical security alerts are escalated to the incident commander.

## Vulnerability management
The engineering team reviews dependency and container vulnerability scan results weekly. Critical vulnerabilities are targeted for remediation within 7 calendar days, high vulnerabilities within 30 calendar days, and medium vulnerabilities within 90 calendar days. Exceptions require documented risk acceptance.

## Change management
Application changes are tracked through pull requests. Each production change requires code review, automated tests, and approval before deployment. Emergency changes must be documented after implementation and reviewed in the next engineering retrospective. Rollback instructions are maintained for critical services.

## Vendor management
New vendors that process customer data require security review before onboarding. The review includes data processed, access scope, contract status, DPA status, subprocessor review, and business owner approval. Critical vendors are reviewed annually.

## Availability and continuity
Production services are monitored for uptime and error rates. Backups are performed daily for critical databases. Backup restore testing is performed quarterly. Target recovery time objective for core customer systems is 8 hours and target recovery point objective is 24 hours.
