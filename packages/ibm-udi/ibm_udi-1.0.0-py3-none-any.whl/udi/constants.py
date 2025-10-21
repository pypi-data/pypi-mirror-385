class DatasiftSDKConstants:
    MILVUS_FEATURE_MAPPINGS = "milvus_feature_mappings"
    NEW_COLLECTION_DEFAULT_FEATURE_MAPPINGS = "new_collection_default_feature_mappings"
    VALID_COLUMNS = "valid_columns"
    AVAILABLE_FEATURES = "available_features"
    ERRORS_RESPONSE_KEY = "errors"
    OPERATOR_PARAMETERS = "parameters"
    COLLECTIONS_COLUMNS = "collection_columns"
    AVAILABLE_COLLECTIONS = "available_collections"
    VECTORDB_MILVUS = "milvusdb_cp4d"
    VECTORDB_ELASTIC = "elasticsearch"

class EnvironmentConstants:
    CPD = "cpd"
    CLOUD_DEV = "cloud-dev"
    CLOUD_TEST = "cloud-test"
    CLOUD_PROD = "cloud-prod"

    ALL_ENVIRONMENTS = {CPD,CLOUD_DEV, CLOUD_TEST, CLOUD_PROD}

class JobStatusConstants:
    QUEUED = "Queued"
    STARTING = "Starting"
    RUNNING = "Running"
    PAUSED = "Paused"
    RESUMING = "Resuming"
    CANCELING = "Canceling"
    CANCELED = "Canceled"
    FAILED = "Failed"
    COMPLETED = "Completed"
    COMPLETED_WITH_ERRORS = "CompletedWithErrors"
    COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
