"""
Wise Decision Engine - Uma abstração moderna para o zen-engine

Facilita o uso de regras de decisão em ambientes distribuídos como Spark/Databricks
com otimizações de cache, tratamento de erros e APIs simplificadas.
"""

from .core import WiseDecisionEngine
from .adapters import (
    DecisionAdapter,
    FileAdapter, 
    DatabricksAdapter,
    DatabaseAdapter,
    create_adapter
)
from .session_cache import (
    SessionCache,
    get_default_session_cache,
    set_default_session_cache
)
from .schema_inference import (
    SchemaInferenceEngine,
    AutoSchemaHelper,
    InferenceStrategy,
    auto_expand_decision_results
)

# Utilitários Spark (importação condicional)
try:
    from .spark_utils import (
        SparkDecisionEvaluator,
        DatabricksHelper,
        create_decision_udf,
        apply_decision_to_dataframe,
        print_migration_guide,
        create_legacy_udf,
        is_databricks_serverless
    )
    SPARK_UTILS_AVAILABLE = True
except ImportError:
    SPARK_UTILS_AVAILABLE = False

__version__ = "0.4.1"

__all__ = [
    "__version__",
    "WiseDecisionEngine",
    "DecisionAdapter",
    "FileAdapter",
    "DatabricksAdapter", 
    "DatabaseAdapter",
    "create_adapter",
    "SessionCache",
    "get_default_session_cache",
    "set_default_session_cache",
    "SchemaInferenceEngine",
    "AutoSchemaHelper",
    "InferenceStrategy",
    "auto_expand_decision_results",
]

# Adiciona utilitários Spark se disponíveis
if SPARK_UTILS_AVAILABLE:
    __all__.extend([
        "SparkDecisionEvaluator",
        "DatabricksHelper", 
        "create_decision_udf",
        "apply_decision_to_dataframe",
        "print_migration_guide",
        "create_legacy_udf",
        "is_databricks_serverless",
        "SPARK_UTILS_AVAILABLE"
    ])
