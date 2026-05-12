# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Compliance Report: OSFI E-23 & PIPEDA
# MAGIC Generates a shareable HTML compliance report.

# COMMAND ----------

import json
from datetime import datetime

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Audit Results

# COMMAND ----------

try:
    results_json = json.loads(spark.conf.get("governance.audit_results"))
    catalog = spark.conf.get("governance.catalog")
    schema = spark.conf.get("governance.schema")
except Exception:
    print("No audit results found. Run 03_run_audit first.")
    print("Generating sample report for preview...")
    catalog = "main"
    schema = "default"
    results_json = [
        {
            "framework_code": "OSFI_E23",
            "framework_name": "OSFI E-23 Model Risk Management",
            "version": "2023.09",
            "assessed_at": datetime.utcnow().isoformat(),
            "compliance_score": 62.5,
            "total_controls": 16,
            "compliant": 9,
            "partially_compliant": 3,
            "non_compliant": 4,
            "not_assessed": 0,
            "controls": [
                {"control_id": "MRM-1.1", "title": "Enterprise Model Risk Governance", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-1.2", "title": "Roles and Responsibilities", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Insufficient role separation", "severity": "HIGH", "category": "governance",
                     "description": "Model developer also has validator permissions", "remediation": "Separate model development and validation roles"}
                ]},
                {"control_id": "MRM-2.1", "title": "Model Inventory", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-2.2", "title": "Risk Tiering", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Models without risk tier", "severity": "HIGH", "category": "inventory",
                     "description": "3 models lack risk_tier classification", "remediation": "Classify all models as Tier 1/2/3"}
                ]},
                {"control_id": "MRM-3.1", "title": "Development Standards", "status": "PARTIALLY_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Missing development docs", "severity": "MEDIUM", "category": "documentation",
                     "description": "2 models lack documented development standards", "remediation": "Add description and docs tags"}
                ]},
                {"control_id": "MRM-3.2", "title": "Technical Documentation", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-3.3", "title": "Bias and Fairness Testing", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "No bias testing artifacts", "severity": "HIGH", "category": "bias",
                     "description": "Production model deployed without bias test results", "remediation": "Run fairness metrics before promotion"}
                ]},
                {"control_id": "MRM-4.1", "title": "Independent Validation", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "No independent validation", "severity": "HIGH", "category": "validation",
                     "description": "Model promoted without independent validator sign-off", "remediation": "Require validated_by tag"}
                ]},
                {"control_id": "MRM-4.2", "title": "Challenger Models", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-5.1", "title": "Performance Monitoring", "status": "PARTIALLY_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "No monitoring configured", "severity": "MEDIUM", "category": "monitoring",
                     "description": "Production model has no Lakehouse Monitoring table", "remediation": "Enable Databricks Lakehouse Monitoring"}
                ]},
                {"control_id": "MRM-5.2", "title": "Drift Detection", "status": "PARTIALLY_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "No drift detection pipeline", "severity": "MEDIUM", "category": "drift",
                     "description": "No automated drift detection for production models", "remediation": "Configure Lakehouse Monitoring drift metrics"}
                ]},
                {"control_id": "MRM-6.1", "title": "Usage Constraints", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-6.2", "title": "Override Procedures", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-7.1", "title": "Vendor Due Diligence", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-7.2", "title": "Vendor Monitoring", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-8.1", "title": "Board Reporting", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "MRM-8.2", "title": "Escalation Procedures", "status": "COMPLIANT", "findings_count": 0, "findings": []},
            ]
        },
        {
            "framework_code": "PIPEDA",
            "framework_name": "PIPEDA Fair Information Principles",
            "version": "2000_c5_2024",
            "assessed_at": datetime.utcnow().isoformat(),
            "compliance_score": 70.0,
            "total_controls": 15,
            "compliant": 9,
            "partially_compliant": 2,
            "non_compliant": 4,
            "not_assessed": 0,
            "controls": [
                {"control_id": "P1.1", "title": "Privacy Officer Designation", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P1.2", "title": "Third-Party Contracts", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Missing DPA", "severity": "HIGH", "category": "accountability",
                     "description": "External model API provider lacks contractual privacy protections", "remediation": "Execute DPA with all providers"}
                ]},
                {"control_id": "P2.1", "title": "Purpose Documentation", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P2.2", "title": "Purpose Evaluation", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Data repurposed without consent", "severity": "HIGH", "category": "purpose",
                     "description": "Customer data used for model training without re-consent", "remediation": "Obtain fresh consent"}
                ]},
                {"control_id": "P3.1", "title": "Meaningful Consent", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Automated decisions not disclosed", "severity": "CRITICAL", "category": "consent",
                     "description": "ML model makes credit decisions without consent disclosure", "remediation": "Update consent forms"}
                ]},
                {"control_id": "P3.2", "title": "Sensitive Consent", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P4.1", "title": "Data Minimization", "status": "PARTIALLY_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Excessive PII", "severity": "MEDIUM", "category": "pii",
                     "description": "Training dataset contains 12 PII columns; only 3 necessary", "remediation": "Remove unnecessary PII"}
                ]},
                {"control_id": "P5.1", "title": "Access Controls", "status": "NON_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "Overly broad access", "severity": "HIGH", "category": "security",
                     "description": "ALL_PRIVILEGES granted to 5+ principals on PII tables", "remediation": "Apply column-level security"}
                ]},
                {"control_id": "P5.2", "title": "Retention and Disposal", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P6.1", "title": "Data Quality Controls", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P7.1", "title": "Security Safeguards", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P7.2", "title": "Breach Response", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P8.1", "title": "AI Transparency", "status": "PARTIALLY_COMPLIANT", "findings_count": 1, "findings": [
                    {"title": "No model card", "severity": "MEDIUM", "category": "transparency",
                     "description": "Production model lacks public documentation", "remediation": "Create model card"}
                ]},
                {"control_id": "P9.1", "title": "Individual Access Rights", "status": "COMPLIANT", "findings_count": 0, "findings": []},
                {"control_id": "P10.1", "title": "Complaints Process", "status": "COMPLIANT", "findings_count": 0, "findings": []},
            ]
        }
    ]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Generate HTML Report

# COMMAND ----------

def generate_report(results, catalog, schema):
    status_colors = {
        "COMPLIANT": "#22c55e",
        "PARTIALLY_COMPLIANT": "#f59e0b",
        "NON_COMPLIANT": "#ef4444",
        "NOT_ASSESSED": "#94a3b8"
    }
    severity_colors = {
        "CRITICAL": "#dc2626",
        "HIGH": "#ef4444",
        "MEDIUM": "#f59e0b",
        "LOW": "#3b82f6"
    }

    overall_score = sum(r["compliance_score"] for r in results) / len(results) if results else 0
    total_findings = sum(c["findings_count"] for r in results for c in r["controls"])
    critical_count = sum(
        1 for r in results for c in r["controls"]
        for f in c["findings"] if f["severity"] == "CRITICAL"
    )

    def score_color(score):
        if score >= 80: return "#22c55e"
        if score >= 60: return "#f59e0b"
        return "#ef4444"

    frameworks_html = ""
    for r in results:
        controls_html = ""
        for c in r["controls"]:
            color = status_colors[c["status"]]
            findings_html = ""
            for f in c["findings"]:
                sev_color = severity_colors[f["severity"]]
                findings_html += f"""
                <div style="margin:6px 0 6px 20px;padding:10px 14px;background:#fafafa;border-left:3px solid {sev_color};border-radius:4px;font-size:13px;">
                    <div><span style="color:{sev_color};font-weight:600;">[{f["severity"]}]</span> {f["description"]}</div>
                    <div style="margin-top:4px;color:#6b7280;"><b>Remediation:</b> {f["remediation"]}</div>
                </div>"""
            controls_html += f"""
            <div style="margin:4px 0;padding:10px 14px;background:white;border-radius:6px;border:1px solid #e5e7eb;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">{c["status"].replace("_"," ")}</span>
                    <span style="font-weight:600;color:#1e293b;">{c["control_id"]}</span>
                    <span style="color:#475569;">{c["title"]}</span>
                    {"<span style='color:#94a3b8;font-size:12px;'>(" + str(c["findings_count"]) + " findings)</span>" if c["findings_count"] else ""}
                </div>
                {findings_html}
            </div>"""

        sc = score_color(r["compliance_score"])
        frameworks_html += f"""
        <div style="margin:24px 0;padding:20px;background:#f8fafc;border-radius:10px;border:1px solid #e2e8f0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
                <div>
                    <h2 style="margin:0;color:#1e293b;">{r["framework_name"]}</h2>
                    <div style="color:#64748b;font-size:13px;">Version {r["version"]} | {r["assessed_at"][:19]}</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:36px;font-weight:700;color:{sc};">{r["compliance_score"]}%</div>
                    <div style="font-size:12px;color:#64748b;">Compliance Score</div>
                </div>
            </div>
            <div style="display:flex;gap:16px;margin-bottom:16px;">
                <div style="flex:1;text-align:center;padding:8px;background:#dcfce7;border-radius:6px;">
                    <div style="font-size:20px;font-weight:700;color:#16a34a;">{r["compliant"]}</div>
                    <div style="font-size:11px;color:#16a34a;">Compliant</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:#fef3c7;border-radius:6px;">
                    <div style="font-size:20px;font-weight:700;color:#d97706;">{r["partially_compliant"]}</div>
                    <div style="font-size:11px;color:#d97706;">Partial</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:#fee2e2;border-radius:6px;">
                    <div style="font-size:20px;font-weight:700;color:#dc2626;">{r["non_compliant"]}</div>
                    <div style="font-size:11px;color:#dc2626;">Non-Compliant</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px;background:#f1f5f9;border-radius:6px;">
                    <div style="font-size:20px;font-weight:700;color:#64748b;">{r["not_assessed"]}</div>
                    <div style="font-size:11px;color:#64748b;">Not Assessed</div>
                </div>
            </div>
            {controls_html}
        </div>"""

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:960px;margin:0 auto;padding:24px;">
        <div style="text-align:center;margin-bottom:32px;padding:24px;background:linear-gradient(135deg,#1e293b,#334155);border-radius:12px;color:white;">
            <h1 style="margin:0 0 8px 0;font-size:24px;">Databricks Governance Compliance Report</h1>
            <div style="font-size:14px;opacity:0.8;">OSFI E-23 & PIPEDA | {catalog}.{schema}</div>
            <div style="font-size:13px;opacity:0.6;margin-top:4px;">Generated {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</div>
        </div>

        <div style="display:flex;gap:16px;margin-bottom:24px;">
            <div style="flex:1;text-align:center;padding:20px;background:white;border-radius:10px;border:1px solid #e2e8f0;">
                <div style="font-size:42px;font-weight:700;color:{score_color(overall_score)};">{overall_score:.1f}%</div>
                <div style="font-size:13px;color:#64748b;">Overall Compliance</div>
            </div>
            <div style="flex:1;text-align:center;padding:20px;background:white;border-radius:10px;border:1px solid #e2e8f0;">
                <div style="font-size:42px;font-weight:700;color:#1e293b;">{total_findings}</div>
                <div style="font-size:13px;color:#64748b;">Total Findings</div>
            </div>
            <div style="flex:1;text-align:center;padding:20px;background:white;border-radius:10px;border:1px solid #e2e8f0;">
                <div style="font-size:42px;font-weight:700;color:{"#dc2626" if critical_count else "#22c55e"};">{critical_count}</div>
                <div style="font-size:13px;color:#64748b;">Critical Findings</div>
            </div>
        </div>

        {frameworks_html}

        <div style="text-align:center;margin-top:32px;padding:16px;color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;">
            PaavanAadi Labs | AI Governance Audit Framework | {datetime.utcnow().strftime("%Y")}
        </div>
    </div>"""
    return html

# COMMAND ----------

report_html = generate_report(results_json, catalog, schema)
displayHTML(report_html)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Export Report

# COMMAND ----------

report_path = f"/Workspace/Users/{spark.conf.get('spark.databricks.notebook.username', 'shared')}/governance_report_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.html"

try:
    full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Governance Report</title>
    <style>body{{margin:0;padding:20px;background:#f1f5f9;}}</style></head><body>{report_html}</body></html>"""
    dbutils.fs.put(report_path, full_html, overwrite=True)
    print(f"Report saved to: {report_path}")
except Exception as e:
    print(f"Could not save to workspace: {e}")
    print("Use the displayed HTML above or copy from the cell output.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Quick Summary for Stakeholders

# COMMAND ----------

print("=" * 60)
print("  GOVERNANCE COMPLIANCE SUMMARY")
print("=" * 60)
for r in results_json:
    status = "PASS" if r["compliance_score"] >= 80 else "REVIEW" if r["compliance_score"] >= 60 else "FAIL"
    print(f"\n  {r['framework_code']}: {r['compliance_score']}% [{status}]")
    print(f"    {r['compliant']}/{r['total_controls']} controls compliant")
    if r["non_compliant"]:
        print(f"    {r['non_compliant']} controls require immediate attention")
    critical = [f for c in r["controls"] for f in c["findings"] if f["severity"] == "CRITICAL"]
    if critical:
        print(f"    CRITICAL: {critical[0]['description']}")
print(f"\n{'=' * 60}")
