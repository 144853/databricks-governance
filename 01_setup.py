# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Setup: Databricks Governance for OSFI E-23 & PIPEDA
# MAGIC Install dependencies and configure audit parameters.

# COMMAND ----------

# MAGIC %pip install pyyaml jinja2 --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configure Audit Scope
# MAGIC Set your Unity Catalog target and audit options via widgets.

# COMMAND ----------

dbutils.widgets.text("catalog", "main", "Unity Catalog Name")
dbutils.widgets.text("schema", "default", "Schema Name")
dbutils.widgets.dropdown("framework", "BOTH", ["OSFI_E23", "PIPEDA", "BOTH"], "Regulatory Framework")
dbutils.widgets.dropdown("audit_mode", "LIVE", ["LIVE", "DEMO"], "Audit Mode")

# COMMAND ----------

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
framework = dbutils.widgets.get("framework")
audit_mode = dbutils.widgets.get("audit_mode")

print(f"Audit scope: {catalog}.{schema}")
print(f"Framework:   {framework}")
print(f"Mode:        {audit_mode}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Workspace Access

# COMMAND ----------

if audit_mode == "LIVE":
    try:
        tables = spark.sql(f"SHOW TABLES IN {catalog}.{schema}").collect()
        print(f"Found {len(tables)} tables in {catalog}.{schema}")
    except Exception as e:
        print(f"Cannot access {catalog}.{schema}: {e}")
        print("Switch to DEMO mode or check permissions.")
else:
    print("Running in DEMO mode — no workspace access required.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify MLflow Access

# COMMAND ----------

if audit_mode == "LIVE":
    import mlflow
    client = mlflow.MlflowClient()
    try:
        models = client.search_registered_models(max_results=5)
        print(f"MLflow connected — found {len(models)} registered models")
    except Exception as e:
        print(f"MLflow access issue: {e}")
else:
    print("Skipping MLflow check in DEMO mode.")

# COMMAND ----------

print("Setup complete. Proceed to 02_governance_checks.")
