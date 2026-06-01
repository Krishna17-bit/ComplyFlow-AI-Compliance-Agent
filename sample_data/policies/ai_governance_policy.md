# AI Governance Policy

Owner: AI Governance Committee  
Review cadence: Semiannual

## AI system inventory
All internal and customer-facing AI systems must be recorded in the AI system inventory before production release. The inventory includes system owner, business purpose, model or vendor dependency, input data categories, output users, deployment context, and review status.

## Risk classification
AI use cases are classified before release as low, medium, or high impact. Classification considers customer impact, automated decision-making, sensitive data use, safety impact, bias risk, and whether the output is used without human review.

## Data governance
AI teams must document source datasets, allowed data categories, retention expectations, known limitations, and access restrictions. Customer confidential information must not be used for model training unless the contract and product terms explicitly permit it.

## Evaluation and validation
AI systems require pre-release evaluation for intended use, factuality, robustness, harmful output, bias indicators, and security abuse cases. Evaluation results must be attached to the AI inventory record.

## Human oversight
AI outputs used for security, compliance, hiring, financial, health, or customer-impacting decisions require human review before action. Users must be able to escalate incorrect or harmful outputs.

## Transparency
Customer-facing AI features must include clear notice when users interact with AI-generated content. Product documentation must describe limitations, human review expectations, and escalation process.

## Monitoring
Owners review AI performance, misuse reports, drift indicators, and incidents after release. Material incidents are escalated to the AI Governance Committee and tracked until corrective action is complete.

## AI security
AI systems must include prompt injection defenses, sensitive data handling controls, access restrictions, logging, and abuse monitoring. Retrieval-augmented systems must cite sources and avoid unsupported claims.
