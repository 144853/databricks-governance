# Databricks Governance — OSFI E-23 & PIPEDA

Automated compliance toolkit for auditing Databricks workspaces against Canadian regulatory requirements. Runs natively as Databricks notebooks — no external agents or sidecars.

Built for **banks, insurers, and credit unions** operating ML pipelines on the Databricks Lakehouse.

## What It Does

| | |
|---|---|
| **31 controls** | 16 OSFI E-23 (Model Risk Management) + 15 PIPEDA (Fair Information Principles) |
| **Databricks-native** | Queries Unity Catalog, MLflow, grants, and serving endpoints directly |
| **Two modes** | LIVE (real workspace audit) and DEMO (sample findings for presentations) |
| **Audit report** | HTML compliance dashboard with scores, findings, and remediation guidance |

## Quick Start

1. Import the four `.py` files into your Databricks workspace (File > Import)
2. Run **01_setup** to install dependencies and verify access
3. Set your catalog/schema via notebook widgets
4. Run **03_run_audit** to execute all 31 checks
5. Run **04_report_dashboard** to generate the HTML report

For demos without workspace access, set the **Audit Mode** widget to `DEMO`.

## Repository Contents

```
├── 01_setup.py                              # Dependencies + workspace verification
├── 02_governance_checks.py                  # Core engine: OSFIChecks + PIPEDAChecks
├── 03_run_audit.py                          # Audit orchestrator + findings summary
├── 04_report_dashboard.py                   # HTML report generator
├── config.yaml                              # Control definitions + thresholds
├── onepager.html                            # Printable one-page overview
└── Databricks_Governance_Presentation.docx  # Full presentation document
```

## OSFI E-23 Controls (16)

| Control Group | IDs | What We Check |
|---|---|---|
| **MRM-1: Governance** | MRM-1.1, 1.2 | Governance framework tags on catalog, role separation via grants |
| **MRM-2: Inventory** | MRM-2.1, 2.2 | Model registry completeness (owner, risk tier, purpose), risk tiering |
| **MRM-3: Development** | MRM-3.1–3.3 | Development docs, technical documentation, bias/fairness testing |
| **MRM-4: Validation** | MRM-4.1, 4.2 | Independent validation evidence, challenger model benchmarking |
| **MRM-5: Monitoring** | MRM-5.1, 5.2 | Lakehouse Monitoring tables, automated drift detection |
| **MRM-6: Use & Limits** | MRM-6.1, 6.2 | Usage constraints, override procedure tracking |
| **MRM-7: Vendor** | MRM-7.1, 7.2 | Third-party model due diligence, ongoing vendor monitoring |
| **MRM-8: Reporting** | MRM-8.1, 8.2 | Board reporting cadence, escalation procedures |

## PIPEDA Controls (15)

| Principle | IDs | What We Check |
|---|---|---|
| **P1: Accountability** | P1.1, P1.2 | Privacy officer designation, third-party DPAs |
| **P2: Purposes** | P2.1, P2.2 | Purpose documentation, re-consent for data repurposing |
| **P3: Consent** | P3.1, P3.2 | Meaningful consent for automated decisions, sensitive data consent |
| **P4: Collection** | P4.1 | PII column detection, data minimization |
| **P5: Retention** | P5.1, P5.2 | Access control audit, retention schedules and disposal |
| **P6: Accuracy** | P6.1 | Data quality controls for personal information |
| **P7: Safeguards** | P7.1, P7.2 | Encryption/access controls, breach detection and notification |
| **P8: Openness** | P8.1 | AI transparency disclosure in privacy policies |
| **P9: Access** | P9.1 | Data subject access requests within 30 days |
| **P10: Compliance** | P10.1 | Complaints process for AI decision challenges |

## Compliance Scoring

```
score = (compliant + 0.5 × partially_compliant) / total_controls × 100
```

| Finding Severity | Control Status | Score Credit |
|---|---|---|
| None | COMPLIANT | 1.0 |
| LOW / MEDIUM | PARTIALLY_COMPLIANT | 0.5 |
| HIGH / CRITICAL | NON_COMPLIANT | 0.0 |

When multiple findings hit the same control, worst-case status wins.

## Databricks Data Sources

The toolkit queries these native Databricks APIs and metadata:

- **Unity Catalog** — table/column tags, information_schema for PII scanning
- **Grants** — `SHOW GRANTS` for access control auditing
- **MLflow Registry** — model tags (owner, risk_tier, validated_by, bias_test_passed)
- **MLflow Runs** — parameters and metrics for documentation completeness
- **Serving Endpoints** — vendor/foundation model detection
- **Lakehouse Monitoring** — drift and performance tracking
- **Delta Properties** — retention settings for disposal compliance

## Requirements

- Databricks Runtime 14.0+ (or 15.x ML Runtime)
- Unity Catalog enabled
- Workspace admin or metastore admin for full coverage
- Python packages: `pyyaml`, `jinja2` (installed automatically by 01_setup)

## License

Apache License 2.0 — see [LICENSE](LICENSE)

## Author

**Ashoka Sangapallar** — Databricks/AI Specialist
Databricks Certified
