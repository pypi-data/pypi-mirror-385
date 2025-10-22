# Forbidden ECS fields in IFS logging standard
FORBIDDEN_FIELDS = {
    "_id",
    "_index",
    "_score",
    "stream",
    "kubernetes",
}

# Field normalization mapping
FIELD_RENAMES = {
    "timestamp": "_timestamp",
    "hostName": "host.name",
}

# Contextual environment variables for Tekton/K8s
CONTEXT_ENV_VARS = [
    "TEKTON_PIPELINE_NAME",
    "TEKTON_TASK_NAME",
    "TEKTON_STEP_NAME",
    "POD_NAME",
    "NAMESPACE",
]
