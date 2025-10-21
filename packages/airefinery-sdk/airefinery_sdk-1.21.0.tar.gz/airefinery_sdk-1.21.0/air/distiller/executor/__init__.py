"""
This package provides various Executor classes for handling different agent types.
Classes are imported lazily to avoid slow imports of third-party libraries unless needed.
"""

import importlib

# Map the "agent_class" string to the executor's module and class name.
# If your Executor class sets "agent_class = 'executor'", you cannot safely resolve
# that attribute without first importing the module (defeating the lazy load).
# So we declare the mapping ourselves:
_AGENT_CLASS_MAP = {
    "CustomAgent": ("air.distiller.executor.executor", "Executor"),
    "CBInsightsAgent": (
        "air.distiller.executor.cb_insights_executor",
        "CBInsightsExecutor",
    ),
    "AnalyticsAgent": (
        "air.distiller.executor.analytics_executor",
        "AnalyticsExecutor",
    ),
    "ToolUseAgent": ("air.distiller.executor.tool_executor", "ToolExecutor"),
    "GoogleAgent": ("air.distiller.executor.google_executor", "GoogleExecutor"),
    "AzureAIAgent": ("air.distiller.executor.azure_executor", "AzureExecutor"),
    "MCPClientAgent": ("air.distiller.executor.mcp_executor", "MCPExecutor"),
    "WriterAIAgent": ("air.distiller.executor.writer_executor", "WriterExecutor"),
    "A2AClientAgent": ("air.distiller.executor.a2a_executor", "A2AExecutor"),
    "SalesforceAgent": (
        "air.distiller.executor.salesforce_executor",
        "SalesforceExecutor",
    ),
    "ResearchAgent": (
        "air.distiller.executor.vector_search_executor",
        "CustomVectorSearchExecutor",
    ),
    "AmazonBedrockAgent": (
        "air.distiller.executor.amazon_bedrock_executor",
        "AmazonBedrockExecutor",
    ),
    "DatabricksAgent": (
        "air.distiller.executor.databricks_executor",
        "DatabricksExecutor",
    ),
    "HumanAgent": ("air.distiller.executor.human_executor", "HumanExecutor"),
    "SAPAgent": (
        "air.distiller.executor.sap_executor",
        "SAPExecutor",
    ),
    "DeepResearchAgent": (
        "air.distiller.executor.deep_research_executor",
        "DeepResearchExecutor",
    ),
    "PegaAgent": (
        "air.distiller.executor.pega_executor",
        "PegaExecutor",
    ),
    "ServiceNowAgent": (
        "air.distiller.executor.servicenow_executor",
        "ServiceNowExecutor",
    ),
    "SnowflakeAgent": (
        "air.distiller.executor.snowflake_executor",
        "SnowflakeExecutor",
    ),
    "WolframAgent": (
        "air.distiller.executor.wolfram_executor",
        "WolframExecutor",
    ),
}

# Cache for already-imported executor classes, so we import them only once.
_EXECUTOR_CLASS_CACHE = {}


def get_executor_class(agent_class: str):
    """
    Given an agent_class string (e.g. "executor" or "analytics"),
    lazily import and return the corresponding Executor class.
    """
    if agent_class not in _AGENT_CLASS_MAP:
        raise ValueError(f"Unknown agent_class '{agent_class}'")

    if agent_class not in _EXECUTOR_CLASS_CACHE:
        module_name, class_name = _AGENT_CLASS_MAP[agent_class]
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        _EXECUTOR_CLASS_CACHE[agent_class] = cls

    return _EXECUTOR_CLASS_CACHE[agent_class]


def get_executor(agent_class: str, *args, **kwargs):
    """
    Create an instance of the executor for the given agent_class,
    passing along any constructor arguments.
    """
    executor_cls = get_executor_class(agent_class)
    return executor_cls(*args, **kwargs)


def get_all_executor_agents():
    """
    Return a list (or set) of all possible agent_class keys.
    These are the recognized executors you could potentially instantiate.
    """
    return list(_AGENT_CLASS_MAP.keys())
