# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Run Audit: OSFI E-23 & PIPEDA Governance
# MAGIC Orchestrates the full audit and displays results.

# COMMAND ----------

# MAGIC %run ./02_governance_checks

# COMMAND ----------

import yaml, json

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Configuration

# COMMAND ----------

config_yaml = """
workspace:
  catalog: "main"
  schema: "default"

thresholds:
  bias_disparate_impact: 0.8
  drift_psi_critical: 0.25
  drift_psi_warning: 0.10
  stale_credential_days: 90
  model_review_days: 180

osfi_e23:
  version: "2023.09"
  controls:
    MRM-1.1:
      title: "Enterprise Model Risk Governance Framework"
      check: "check_governance_framework"
      severity_if_missing: "HIGH"
    MRM-1.2:
      title: "Roles and Responsibilities"
      check: "check_roles_separation"
      severity_if_missing: "HIGH"
    MRM-2.1:
      title: "Model Inventory"
      check: "check_model_inventory"
      severity_if_missing: "CRITICAL"
    MRM-2.2:
      title: "Risk Tiering"
      check: "check_risk_tiering"
      severity_if_missing: "HIGH"
    MRM-3.1:
      title: "Development Standards"
      check: "check_development_docs"
      severity_if_missing: "MEDIUM"
    MRM-3.2:
      title: "Technical Documentation"
      check: "check_technical_docs"
      severity_if_missing: "MEDIUM"
    MRM-3.3:
      title: "Bias and Fairness Testing"
      check: "check_bias_testing"
      severity_if_missing: "HIGH"
    MRM-4.1:
      title: "Independent Validation"
      check: "check_independent_validation"
      severity_if_missing: "HIGH"
    MRM-4.2:
      title: "Challenger Models"
      check: "check_challenger_models"
      severity_if_missing: "MEDIUM"
    MRM-5.1:
      title: "Performance Monitoring"
      check: "check_performance_monitoring"
      severity_if_missing: "HIGH"
    MRM-5.2:
      title: "Drift Detection"
      check: "check_drift_detection"
      severity_if_missing: "HIGH"
    MRM-6.1:
      title: "Usage Constraints"
      check: "check_usage_constraints"
      severity_if_missing: "MEDIUM"
    MRM-6.2:
      title: "Override Procedures"
      check: "check_override_procedures"
      severity_if_missing: "MEDIUM"
    MRM-7.1:
      title: "Vendor Model Due Diligence"
      check: "check_vendor_due_diligence"
      severity_if_missing: "HIGH"
    MRM-7.2:
      title: "Vendor Model Monitoring"
      check: "check_vendor_monitoring"
      severity_if_missing: "MEDIUM"
    MRM-8.1:
      title: "Board Reporting"
      check: "check_board_reporting"
      severity_if_missing: "MEDIUM"
    MRM-8.2:
      title: "Escalation Procedures"
      check: "check_escalation_procedures"
      severity_if_missing: "MEDIUM"

pipeda:
  version: "2000_c5_2024"
  controls:
    P1.1:
      title: "Privacy Officer Designation"
      check: "check_privacy_officer"
      severity_if_missing: "HIGH"
    P1.2:
      title: "Third-Party Contractual Protection"
      check: "check_third_party_contracts"
      severity_if_missing: "HIGH"
    P2.1:
      title: "Purpose Documentation"
      check: "check_purpose_docs"
      severity_if_missing: "MEDIUM"
    P2.2:
      title: "New Purpose Evaluation"
      check: "check_purpose_evaluation"
      severity_if_missing: "HIGH"
    P3.1:
      title: "Meaningful Consent"
      check: "check_meaningful_consent"
      severity_if_missing: "CRITICAL"
    P3.2:
      title: "Sensitive Information Consent"
      check: "check_sensitive_consent"
      severity_if_missing: "CRITICAL"
    P4.1:
      title: "Data Minimization"
      check: "check_data_minimization"
      severity_if_missing: "MEDIUM"
    P5.1:
      title: "Access Controls and Audit Logs"
      check: "check_access_controls"
      severity_if_missing: "HIGH"
    P5.2:
      title: "Retention and Disposal"
      check: "check_retention_policy"
      severity_if_missing: "HIGH"
    P6.1:
      title: "Data Quality Controls"
      check: "check_data_quality"
      severity_if_missing: "MEDIUM"
    P7.1:
      title: "Security Safeguards"
      check: "check_security_safeguards"
      severity_if_missing: "HIGH"
    P7.2:
      title: "Breach Detection and Notification"
      check: "check_breach_response"
      severity_if_missing: "CRITICAL"
    P8.1:
      title: "AI Transparency"
      check: "check_ai_transparency"
      severity_if_missing: "MEDIUM"
    P9.1:
      title: "Individual Access Rights"
      check: "check_access_rights"
      severity_if_missing: "HIGH"
    P10.1:
      title: "Complaints Process"
      check: "check_complaints_process"
      severity_if_missing: "MEDIUM"
"""

config = yaml.safe_load(config_yaml)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run Audit

# COMMAND ----------

try:
    catalog = dbutils.widgets.get("catalog")
    schema = dbutils.widgets.get("schema")
    framework = dbutils.widgets.get("framework")
    audit_mode = dbutils.widgets.get("audit_mode")
except Exception:
    catalog = "main"
    schema = "default"
    framework = "BOTH"
    audit_mode = "DEMO"

print(f"Running {framework} audit on {catalog}.{schema} in {audit_mode} mode...")

auditor = GovernanceAuditor(spark, catalog, schema, audit_mode)
results = auditor.run_all(config, framework)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

for assessment in results:
    print(f"\n{'='*60}")
    print(f"  {assessment.framework_name}")
    print(f"  Version: {assessment.version}")
    print(f"  Assessed: {assessment.assessed_at}")
    print(f"{'='*60}")
    print(f"  Compliance Score: {assessment.compliance_score}%")
    print(f"  Total Controls:  {assessment.total_controls}")
    print(f"  ✓ Compliant:            {assessment.compliant}")
    print(f"  ~ Partially Compliant:  {assessment.partially_compliant}")
    print(f"  ✗ Non-Compliant:        {assessment.non_compliant}")
    print(f"  ? Not Assessed:         {assessment.not_assessed}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Control Details

# COMMAND ----------

for assessment in results:
    print(f"\n--- {assessment.framework_code} Controls ---")
    for ctrl in assessment.controls:
        icon = {"COMPLIANT": "✓", "PARTIALLY_COMPLIANT": "~",
                "NON_COMPLIANT": "✗", "NOT_ASSESSED": "?"}[ctrl.status.value]
        print(f"  {icon} {ctrl.control_id}: {ctrl.title} [{ctrl.status.value}]")
        for f in ctrl.findings:
            print(f"      [{f.severity.value}] {f.description}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Findings Detail

# COMMAND ----------

all_findings = []
for assessment in results:
    for ctrl in assessment.controls:
        for f in ctrl.findings:
            all_findings.append({
                "framework": assessment.framework_code,
                "control_id": f.control_id,
                "title": f.title,
                "severity": f.severity.value,
                "category": f.category,
                "description": f.description,
                "remediation": f.remediation
            })

if all_findings:
    df_findings = spark.createDataFrame(all_findings)
    display(df_findings.orderBy("severity", "framework", "control_id"))
else:
    print("No findings — full compliance!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Store Results for Report

# COMMAND ----------

import json

results_json = []
for a in results:
    fw = {
        "framework_code": a.framework_code,
        "framework_name": a.framework_name,
        "version": a.version,
        "assessed_at": a.assessed_at,
        "compliance_score": a.compliance_score,
        "total_controls": a.total_controls,
        "compliant": a.compliant,
        "partially_compliant": a.partially_compliant,
        "non_compliant": a.non_compliant,
        "not_assessed": a.not_assessed,
        "controls": [
            {
                "control_id": c.control_id,
                "title": c.title,
                "status": c.status.value,
                "findings_count": c.findings_count,
                "findings": [
                    {
                        "title": f.title,
                        "severity": f.severity.value,
                        "category": f.category,
                        "description": f.description,
                        "remediation": f.remediation
                    } for f in c.findings
                ]
            } for c in a.controls
        ]
    }
    results_json.append(fw)

spark.conf.set("governance.audit_results", json.dumps(results_json))
spark.conf.set("governance.catalog", catalog)
spark.conf.set("governance.schema", schema)

print(f"Audit complete. {len(all_findings)} findings across {len(results)} frameworks.")
print("Run 04_report_dashboard to generate the HTML report.")
