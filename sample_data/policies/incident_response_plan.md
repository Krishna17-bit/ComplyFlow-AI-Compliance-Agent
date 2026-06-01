# Incident Response Plan

Owner: Security Lead  
Last tabletop exercise: 2026-03-22

## Purpose
The incident response process defines how AcmeCloud detects, triages, investigates, contains, eradicates, recovers from, and reviews security incidents and personal data breaches.

## Roles
Incident Commander: coordinates the response, assigns tasks, and approves external communications.  
Technical Lead: investigates root cause, collects logs, and manages containment.  
Privacy Lead: evaluates personal data impact and notification requirements.  
Communications Lead: prepares customer or regulator notices when required.

## Severity classification
Severity 1 includes confirmed unauthorized access to production customer data, active compromise of production infrastructure, or broad service outage. Severity 2 includes suspected compromise, high-risk vulnerability exploitation, or limited customer impact. Severity 3 includes low-risk events or policy violations.

## Response workflow
1. Detect event through monitoring, employee report, vendor notification, or customer report.
2. Create incident record with owner, timeline, affected systems, data impact, and severity.
3. Contain the issue by disabling accounts, rotating credentials, blocking network access, or rolling back deployment.
4. Preserve logs and evidence.
5. Determine root cause and customer or personal data impact.
6. Recover systems and validate normal operations.
7. Complete post-incident review within 10 business days.

## Breach notification
The Privacy Lead assesses whether a personal data breach creates notification obligations. If notification is required, the decision, timeline, affected data categories, and communication plan are documented. Potential regulator notification is reviewed within 72 hours of becoming aware of a personal data breach.

## Evidence retained
Incident records include timeline, severity, affected assets, data impact, decisions, containment actions, root cause, corrective actions, and post-incident review notes.
