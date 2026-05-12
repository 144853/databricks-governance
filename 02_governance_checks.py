# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Governance Checks: OSFI E-23 & PIPEDA
# MAGIC Core audit engine with 31 check functions mapped to regulatory controls.

# COMMAND ----------

import yaml
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Model

# COMMAND ----------

class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ControlStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_ASSESSED = "NOT_ASSESSED"

@dataclass
class Finding:
    control_id: str
    title: str
    severity: Severity
    category: str
    description: str
    evidence: str = ""
    remediation: str = ""

@dataclass
class ControlAssessment:
    control_id: str
    title: str
    status: ControlStatus
    findings: list = field(default_factory=list)

    @property
    def findings_count(self):
        return len(self.findings)

@dataclass
class FrameworkAssessment:
    framework_code: str
    framework_name: str
    version: str
    assessed_at: str = ""
    controls: list = field(default_factory=list)

    @property
    def total_controls(self):
        return len(self.controls)

    @property
    def compliant(self):
        return sum(1 for c in self.controls if c.status == ControlStatus.COMPLIANT)

    @property
    def non_compliant(self):
        return sum(1 for c in self.controls if c.status == ControlStatus.NON_COMPLIANT)

    @property
    def partially_compliant(self):
        return sum(1 for c in self.controls if c.status == ControlStatus.PARTIALLY_COMPLIANT)

    @property
    def not_assessed(self):
        return sum(1 for c in self.controls if c.status == ControlStatus.NOT_ASSESSED)

    @property
    def compliance_score(self):
        if self.total_controls == 0:
            return 0.0
        score = (self.compliant + 0.5 * self.partially_compliant) / self.total_controls * 100
        return round(score, 1)

# COMMAND ----------

# MAGIC %md
# MAGIC ## OSFI E-23 Checks
# MAGIC Each check returns a list of `Finding` objects. Empty list = compliant.

# COMMAND ----------

class OSFIChecks:
    """Checks for OSFI E-23 Model Risk Management guideline."""

    def __init__(self, spark, catalog, schema, audit_mode="LIVE"):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.audit_mode = audit_mode

    def _demo_findings(self, control_id, title, severity, category, desc, remediation):
        """Generate a sample finding for demo mode."""
        return [Finding(
            control_id=control_id, title=title, severity=Severity(severity),
            category=category, description=desc,
            evidence="[DEMO] Simulated finding for demonstration",
            remediation=remediation
        )]

    def check_governance_framework(self) -> list:
        findings = []
        if self.audit_mode == "DEMO":
            return []  # Assume compliant for demo

        try:
            tags = self.spark.sql(
                f"SELECT * FROM {self.catalog}.information_schema.catalog_tags "
                f"WHERE tag_name = 'governance_framework_approved'"
            ).collect()
            if not tags:
                findings.append(Finding(
                    control_id="MRM-1.1",
                    title="No governance framework tag on catalog",
                    severity=Severity.HIGH, category="governance",
                    description=f"Catalog '{self.catalog}' lacks a 'governance_framework_approved' tag",
                    remediation="Tag your catalog: ALTER CATALOG SET TAGS ('governance_framework_approved' = 'true')"
                ))
        except Exception:
            findings.append(Finding(
                control_id="MRM-1.1",
                title="Cannot verify governance framework",
                severity=Severity.MEDIUM, category="governance",
                description="Unable to query catalog tags for governance framework verification",
                remediation="Ensure catalog tag access and set governance_framework_approved tag"
            ))
        return findings

    def check_roles_separation(self) -> list:
        findings = []
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-1.2", "Insufficient role separation", Severity.HIGH, "governance",
                "Model developer also has validator permissions",
                "Separate model development and validation roles in Unity Catalog"
            )
        try:
            grants = self.spark.sql(
                f"SHOW GRANTS ON CATALOG {self.catalog}"
            ).collect()
            admins = [g for g in grants if "ALL_PRIVILEGES" in str(g)]
            if len(admins) > 3:
                findings.append(Finding(
                    control_id="MRM-1.2",
                    title="Excessive admin access on catalog",
                    severity=Severity.HIGH, category="governance",
                    description=f"{len(admins)} principals have ALL_PRIVILEGES on catalog",
                    remediation="Reduce to max 3 admins; use granular grants for developers/validators"
                ))
        except Exception:
            pass
        return findings

    def check_model_inventory(self) -> list:
        findings = []
        if self.audit_mode == "DEMO":
            return []

        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                tags = {t.key: t.value for t in (m.tags or [])}
                missing = []
                for required in ["owner", "risk_tier", "purpose", "validation_status"]:
                    if required not in tags:
                        missing.append(required)
                if missing:
                    findings.append(Finding(
                        control_id="MRM-2.1",
                        title=f"Incomplete model registry entry: {m.name}",
                        severity=Severity.HIGH, category="inventory",
                        description=f"Model '{m.name}' missing tags: {', '.join(missing)}",
                        remediation=f"Add required tags to model '{m.name}' in MLflow registry"
                    ))
        except Exception:
            findings.append(Finding(
                control_id="MRM-2.1",
                title="Cannot access model registry",
                severity=Severity.MEDIUM, category="inventory",
                description="Unable to query MLflow model registry",
                remediation="Verify MLflow access permissions"
            ))
        return findings

    def check_risk_tiering(self) -> list:
        findings = []
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-2.2", "Models without risk tier", Severity.HIGH, "inventory",
                "3 models lack risk_tier classification",
                "Classify all models as Tier 1 (critical), Tier 2 (significant), or Tier 3 (low)"
            )
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            untiered = [m.name for m in models
                        if "risk_tier" not in {t.key for t in (m.tags or [])}]
            if untiered:
                findings.append(Finding(
                    control_id="MRM-2.2",
                    title=f"{len(untiered)} models without risk tier",
                    severity=Severity.HIGH, category="inventory",
                    description=f"Untiered models: {', '.join(untiered[:5])}",
                    remediation="Assign risk_tier tag (Tier1/Tier2/Tier3) to all models"
                ))
        except Exception:
            pass
        return findings

    def check_development_docs(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-3.1", "Missing development documentation", Severity.MEDIUM, "documentation",
                "2 models lack documented development standards",
                "Add description and development_docs tag to MLflow model entries"
            )
        findings = []
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                if not m.description or len(m.description) < 50:
                    findings.append(Finding(
                        control_id="MRM-3.1",
                        title=f"Insufficient documentation: {m.name}",
                        severity=Severity.MEDIUM, category="documentation",
                        description=f"Model '{m.name}' has no or minimal description",
                        remediation="Add comprehensive model description covering data, features, methodology"
                    ))
        except Exception:
            pass
        return findings

    def check_technical_docs(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        findings = []
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                versions = client.search_model_versions(f"name='{m.name}'")
                for v in versions:
                    if v.current_stage in ("Production", "Staging"):
                        run = client.get_run(v.run_id) if v.run_id else None
                        if run and len(run.data.params) < 3:
                            findings.append(Finding(
                                control_id="MRM-3.2",
                                title=f"Sparse run parameters: {m.name} v{v.version}",
                                severity=Severity.MEDIUM, category="documentation",
                                description="Production model has fewer than 3 logged parameters",
                                remediation="Log all hyperparameters, data sources, and preprocessing steps"
                            ))
        except Exception:
            pass
        return findings

    def check_bias_testing(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-3.3", "No bias testing artifacts", Severity.HIGH, "bias",
                "Production model deployed without bias test results",
                "Run fairness metrics (disparate impact, demographic parity) before promotion"
            )
        findings = []
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                tags = {t.key: t.value for t in (m.tags or [])}
                if tags.get("risk_tier") in ("Tier1", "Tier2"):
                    if "bias_test_passed" not in tags:
                        findings.append(Finding(
                            control_id="MRM-3.3",
                            title=f"No bias testing for high-risk model: {m.name}",
                            severity=Severity.HIGH, category="bias",
                            description=f"Tier {tags.get('risk_tier', '?')} model lacks bias_test_passed tag",
                            remediation="Conduct bias testing and tag model with results before production"
                        ))
        except Exception:
            pass
        return findings

    def check_independent_validation(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-4.1", "No independent validation evidence", Severity.HIGH, "validation",
                "Model promoted to production without independent validator sign-off",
                "Require validated_by tag from a user outside the development team"
            )
        findings = []
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                tags = {t.key: t.value for t in (m.tags or [])}
                if "validated_by" not in tags:
                    findings.append(Finding(
                        control_id="MRM-4.1",
                        title=f"No independent validation: {m.name}",
                        severity=Severity.HIGH, category="validation",
                        description=f"Model '{m.name}' lacks validated_by tag",
                        remediation="Have an independent validator review and tag the model"
                    ))
        except Exception:
            pass
        return findings

    def check_challenger_models(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_performance_monitoring(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-5.1", "No monitoring configured", Severity.HIGH, "monitoring",
                "Production model has no Lakehouse Monitoring table",
                "Enable Databricks Lakehouse Monitoring on inference tables"
            )
        findings = []
        try:
            import mlflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models(max_results=100)
            for m in models:
                tags = {t.key: t.value for t in (m.tags or [])}
                if "monitoring_table" not in tags:
                    findings.append(Finding(
                        control_id="MRM-5.1",
                        title=f"No monitoring for model: {m.name}",
                        severity=Severity.HIGH, category="monitoring",
                        description=f"Model '{m.name}' has no monitoring_table tag",
                        remediation="Set up Lakehouse Monitoring and tag model with monitoring table name"
                    ))
        except Exception:
            pass
        return findings

    def check_drift_detection(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-5.2", "No drift detection pipeline", Severity.HIGH, "drift",
                "No automated drift detection for production models",
                "Configure Databricks Lakehouse Monitoring drift metrics or custom Evidently pipeline"
            )
        return []

    def check_usage_constraints(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_override_procedures(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_vendor_due_diligence(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "MRM-7.1", "External model without due diligence", Severity.HIGH, "vendor",
                "Foundation model endpoint in use without vendor assessment",
                "Document vendor model assessment including data handling and performance guarantees"
            )
        findings = []
        try:
            endpoints = self.spark.sql(
                "SELECT * FROM system.serving.served_entities"
            ).collect()
            for ep in endpoints:
                if "external" in str(ep).lower() or "foundation" in str(ep).lower():
                    findings.append(Finding(
                        control_id="MRM-7.1",
                        title=f"External model endpoint requires due diligence",
                        severity=Severity.HIGH, category="vendor",
                        description=f"Serving endpoint uses external model — verify vendor assessment",
                        remediation="Complete vendor due diligence form for all third-party model APIs"
                    ))
        except Exception:
            pass
        return findings

    def check_vendor_monitoring(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_board_reporting(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_escalation_procedures(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

# COMMAND ----------

# MAGIC %md
# MAGIC ## PIPEDA Checks

# COMMAND ----------

class PIPEDAChecks:
    """Checks for PIPEDA Fair Information Principles."""

    def __init__(self, spark, catalog, schema, audit_mode="LIVE"):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.audit_mode = audit_mode

    def _demo_findings(self, control_id, title, severity, category, desc, remediation):
        return [Finding(
            control_id=control_id, title=title, severity=Severity(severity),
            category=category, description=desc,
            evidence="[DEMO] Simulated finding for demonstration",
            remediation=remediation
        )]

    def check_privacy_officer(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_third_party_contracts(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P1.2", "Missing third-party data processing agreement", Severity.HIGH, "accountability",
                "External model API provider lacks contractual privacy protections",
                "Execute DPA with all third-party AI/ML service providers"
            )
        return []

    def check_purpose_docs(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_purpose_evaluation(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P2.2", "Data repurposed without consent re-evaluation", Severity.HIGH, "purpose",
                "Customer data originally collected for service delivery used for model training",
                "Obtain fresh consent before using personal data for new AI/ML purposes"
            )
        return []

    def check_meaningful_consent(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P3.1", "Automated decision-making not disclosed", Severity.CRITICAL, "consent",
                "ML model makes credit decisions without consent disclosure",
                "Update consent forms to disclose automated decision-making and provide opt-out"
            )
        return []

    def check_sensitive_consent(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_data_minimization(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P4.1", "Excessive personal data in training set", Severity.MEDIUM, "pii",
                "Training dataset contains 12 PII columns; only 3 are necessary for model",
                "Remove unnecessary PII columns; use pseudonymization for required fields"
            )
        findings = []
        if self.audit_mode == "LIVE":
            try:
                columns = self.spark.sql(
                    f"SELECT * FROM {self.catalog}.information_schema.columns "
                    f"WHERE table_schema = '{self.schema}'"
                ).collect()
                pii_indicators = ["email", "phone", "ssn", "sin", "address", "dob",
                                  "birth", "passport", "driver", "credit_card", "account_num"]
                for col in columns:
                    col_name = col["column_name"].lower()
                    if any(indicator in col_name for indicator in pii_indicators):
                        tag_check = None
                        try:
                            tag_check = self.spark.sql(
                                f"SELECT * FROM {self.catalog}.information_schema.column_tags "
                                f"WHERE column_name = '{col['column_name']}' "
                                f"AND tag_name = 'pii_justified'"
                            ).collect()
                        except Exception:
                            pass
                        if not tag_check:
                            findings.append(Finding(
                                control_id="P4.1",
                                title=f"Potential PII column without justification: {col['column_name']}",
                                severity=Severity.MEDIUM, category="pii",
                                description=f"Column '{col['table_name']}.{col['column_name']}' may contain PII",
                                evidence=f"Column name matches PII pattern",
                                remediation="Tag column with pii_justified or remove if unnecessary"
                            ))
            except Exception:
                pass
        return findings

    def check_access_controls(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P5.1", "Overly broad table access", Severity.HIGH, "security",
                "ALL_PRIVILEGES granted to 5+ principals on tables with personal data",
                "Apply column-level security and row filters for PII tables"
            )
        findings = []
        if self.audit_mode == "LIVE":
            try:
                tables = self.spark.sql(f"SHOW TABLES IN {self.catalog}.{self.schema}").collect()
                for t in tables:
                    grants = self.spark.sql(
                        f"SHOW GRANTS ON TABLE {self.catalog}.{self.schema}.{t['tableName']}"
                    ).collect()
                    broad_access = [g for g in grants if "ALL_PRIVILEGES" in str(g) or "SELECT" in str(g)]
                    if len(broad_access) > 5:
                        findings.append(Finding(
                            control_id="P5.1",
                            title=f"Broad access on table: {t['tableName']}",
                            severity=Severity.HIGH, category="security",
                            description=f"{len(broad_access)} access grants on {t['tableName']}",
                            remediation="Review and restrict access; apply column masking for PII"
                        ))
            except Exception:
                pass
        return findings

    def check_retention_policy(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P5.2", "No retention policy on PII tables", Severity.HIGH, "retention",
                "Delta tables with personal data have no retention schedule configured",
                "Set delta.deletedFileRetentionDuration and implement automated purge jobs"
            )
        return []

    def check_data_quality(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_security_safeguards(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P7.1", "Unencrypted model serving endpoint", Severity.HIGH, "security",
                "Model serving endpoint accessible without TLS",
                "Enable TLS on all serving endpoints; use customer-managed keys for encryption at rest"
            )
        return []

    def check_breach_response(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

    def check_ai_transparency(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P8.1", "No model card for customer-facing model", Severity.MEDIUM, "transparency",
                "Production model lacks public-facing documentation on AI usage",
                "Create model card documenting purpose, limitations, and data usage"
            )
        return []

    def check_access_rights(self) -> list:
        if self.audit_mode == "DEMO":
            return self._demo_findings(
                "P9.1", "No data subject access request process", Severity.HIGH, "access_rights",
                "No documented process for individuals to access their data in ML systems",
                "Implement DSAR workflow covering training data, inference logs, and model outputs"
            )
        return []

    def check_complaints_process(self) -> list:
        if self.audit_mode == "DEMO":
            return []
        return []

# COMMAND ----------

# MAGIC %md
# MAGIC ## Audit Engine

# COMMAND ----------

class GovernanceAuditor:
    """Orchestrates checks and produces framework assessments."""

    def __init__(self, spark, catalog, schema, audit_mode="LIVE"):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.audit_mode = audit_mode
        self.osfi = OSFIChecks(spark, catalog, schema, audit_mode)
        self.pipeda = PIPEDAChecks(spark, catalog, schema, audit_mode)

    def _run_control(self, checker, check_name, control_id, control_title, severity_if_missing) -> ControlAssessment:
        check_fn = getattr(checker, check_name, None)
        if not check_fn:
            return ControlAssessment(
                control_id=control_id, title=control_title,
                status=ControlStatus.NOT_ASSESSED
            )
        try:
            findings = check_fn()
        except Exception as e:
            findings = [Finding(
                control_id=control_id, title=f"Check failed: {check_name}",
                severity=Severity.MEDIUM, category="error",
                description=str(e), remediation="Investigate check failure"
            )]

        if not findings:
            status = ControlStatus.COMPLIANT
        else:
            worst = max(findings, key=lambda f: list(Severity).index(f.severity))
            if worst.severity in (Severity.HIGH, Severity.CRITICAL):
                status = ControlStatus.NON_COMPLIANT
            else:
                status = ControlStatus.PARTIALLY_COMPLIANT

        return ControlAssessment(
            control_id=control_id, title=control_title,
            status=status, findings=findings
        )

    def run_osfi(self, config) -> FrameworkAssessment:
        controls = []
        for ctrl_id, ctrl_cfg in config["osfi_e23"]["controls"].items():
            ca = self._run_control(
                self.osfi, ctrl_cfg["check"], ctrl_id,
                ctrl_cfg["title"], ctrl_cfg["severity_if_missing"]
            )
            controls.append(ca)

        return FrameworkAssessment(
            framework_code="OSFI_E23",
            framework_name="OSFI E-23 Model Risk Management",
            version=config["osfi_e23"]["version"],
            assessed_at=datetime.utcnow().isoformat(),
            controls=controls
        )

    def run_pipeda(self, config) -> FrameworkAssessment:
        controls = []
        for ctrl_id, ctrl_cfg in config["pipeda"]["controls"].items():
            ca = self._run_control(
                self.pipeda, ctrl_cfg["check"], ctrl_id,
                ctrl_cfg["title"], ctrl_cfg["severity_if_missing"]
            )
            controls.append(ca)

        return FrameworkAssessment(
            framework_code="PIPEDA",
            framework_name="PIPEDA Fair Information Principles",
            version=config["pipeda"]["version"],
            assessed_at=datetime.utcnow().isoformat(),
            controls=controls
        )

    def run_all(self, config, frameworks="BOTH") -> list:
        results = []
        if frameworks in ("OSFI_E23", "BOTH"):
            results.append(self.run_osfi(config))
        if frameworks in ("PIPEDA", "BOTH"):
            results.append(self.run_pipeda(config))
        return results

# COMMAND ----------

print("Governance checks module loaded. Use GovernanceAuditor to run assessments.")
