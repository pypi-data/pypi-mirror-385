import json
import os
from collections.abc import Sequence
from enum import Enum
from typing import Any, Callable, Optional, Union

from freeplay.freeplay import Freeplay
from freeplay.model import InputVariables
from freeplay.resources.prompts import PromptInfo
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
)
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from freeplay_python_langgraph.normalized_message import (
    normalize_message_to_openai_message,
)


class FreeplayOTelAttributes(Enum):
    FREEPLAY_INPUT_VARIABLES = "freeplay.input_variables"
    FREEPLAY_PROMPT_TEMPLATE_VERSION_ID = "freeplay.prompt_template.version.id"
    FREEPLAY_ENVIRONMENT = "freeplay.environment"
    FREEPLAY_TEST_RUN_ID = "freeplay.test_run.id"
    FREEPLAY_TEST_CASE_ID = "freeplay.test_case.id"


class FreeplayLangGraph:
    """Freeplay LangGraph integration with observability and prompt management."""

    client: Freeplay

    def __init__(
        self,
        freeplay_api_url: Optional[str] = None,
        freeplay_api_key: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize Freeplay LangGraph client.

        Args:
            freeplay_api_url: Freeplay API URL (defaults to FREEPLAY_API_URL env var)
            freeplay_api_key: Freeplay API key (defaults to FREEPLAY_API_KEY env var)
            project_id: Freeplay project ID (defaults to FREEPLAY_PROJECT_ID env var)

        Example:
            # Initialize from environment variables
            freeplay = FreeplayLangGraph()

            # Or with explicit configuration
            freeplay = FreeplayLangGraph(
                freeplay_api_url="https://api.freeplay.ai",
                freeplay_api_key="fp_...",
                project_id="proj_123",
            )
        """
        # Get from environment if not provided
        freeplay_api_url = freeplay_api_url or os.environ.get("FREEPLAY_API_URL", "")
        freeplay_api_key = freeplay_api_key or os.environ.get("FREEPLAY_API_KEY", "")
        self.project_id = project_id or os.environ.get("FREEPLAY_PROJECT_ID", "")

        # Initialize Freeplay client
        self.client = Freeplay(
            freeplay_api_key=freeplay_api_key,
            api_base=freeplay_api_url,
        )

        # Setup OTEL exporter
        exporter = OTLPSpanExporter(
            endpoint=f"{freeplay_api_url}/v0/otel/v1/traces",
            headers={
                "Authorization": f"Bearer {freeplay_api_key}",
                "X-Freeplay-Project-Id": self.project_id,
            },
        )

        tracer_provider = trace_sdk.TracerProvider()
        tracer_provider.add_span_processor(SimpleSpanProcessor(exporter))

        log_spans_to_console = (
            os.environ.get("FREEPLAY_LOG_SPANS_TO_CONSOLE", "false").lower() == "true"
        )

        if log_spans_to_console:
            tracer_provider.add_span_processor(
                SimpleSpanProcessor(ConsoleSpanExporter())
            )

        # Instrument LangChain - this creates spans for LangChain/LangGraph calls
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

    def invoke(  # noqa: PLR0913
        self,
        prompt_name: str,
        variables: InputVariables,
        environment: str = "latest",
        model: Optional[BaseChatModel] = None,
        history: Optional[Sequence[BaseMessage]] = None,
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        test_run_id: Optional[str] = None,
        test_case_id: Optional[str] = None,
        **invoke_kwargs,
    ) -> BaseMessage:
        """
        Invoke a model with a Freeplay-hosted prompt.

        Args:
            prompt_name: Name of the prompt in Freeplay
            variables: Variables to render the prompt template
            environment: Environment to use (e.g., "production", "staging", "latest")
            model: Optional pre-instantiated LangChain model. If not provided,
                   will attempt to auto-create based on Freeplay's model config.
            history: Optional conversation history as LangChain BaseMessage objects
            tools: Optional tools to bind to the model
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            **invoke_kwargs: Additional arguments to pass to model.invoke()

        Returns:
            The model's response

        Raises:
            ImportError: If required provider package not installed
            ValueError: If provider not supported

        Example:
            freeplay = FreeplayLangGraph()

            # Call a Freeplay-hosted prompt with auto-instantiation
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "San Francisco"}
            )

            # Call with conversation history (LangGraph MessagesState)
            from langchain_core.messages import HumanMessage
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "SF"},
                history=[HumanMessage(content="Previous message")]
            )

            # Call with an explicit model
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4", temperature=0)
            response = freeplay.invoke(
                prompt_name="weather-assistant",
                variables={"city": "SF"},
                model=model
            )
        """

        # Normalizing into OpenAI format for Freeplay SDK. Freeplay support provider
        # specific adapters but not LangChain responses directly yet.
        normalized_history = (
            [normalize_message_to_openai_message(msg) for msg in history]
            if history
            else None
        )

        formatted_prompt = self.client.prompts.get_formatted(
            project_id=self.project_id,
            template_name=prompt_name,
            history=normalized_history,
            variables=variables,
            environment=environment,
            flavor_name="openai_chat",
        )

        # If model not provided, auto-create based on provider
        model_instance = model or FreeplayLangGraph.get_model(
            prompt_info=formatted_prompt.prompt_info
        )

        # Prepare invoke config with metadata
        invoke_kwargs = self.get_freeplay_otel_metadata(
            variables=variables,
            prompt_info=formatted_prompt.prompt_info,
            environment=environment,
            test_run_id=test_run_id,
            test_case_id=test_case_id,
            invoke_kwargs=invoke_kwargs,
        )

        if tools:
            model_instance = model_instance.bind_tools(tools)

        # Invoke model with Freeplay metadata
        return model_instance.invoke(formatted_prompt.llm_prompt, **invoke_kwargs)

    def get_freeplay_otel_metadata(  # noqa: PLR0913
        self,
        variables: InputVariables,
        prompt_info: PromptInfo,
        environment: str,
        test_run_id: Optional[str],
        test_case_id: Optional[str],
        invoke_kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prepare invoke config with Freeplay metadata for OpenTelemetry tracing.

        Args:
            variables: Input variables used to render the prompt template
            prompt_info: Prompt information from Freeplay containing template version and model config
            environment: Environment name (e.g., "production", "staging", "latest")
            test_run_id: Optional test run ID for test execution tracking
            test_case_id: Optional test case ID for test execution tracking
            invoke_kwargs: Additional arguments to pass to model.invoke()

        Returns:
            Updated invoke_kwargs with Freeplay metadata added to config.metadata
        """
        # Get or create config matching LangChain's RunnableConfig structure
        config: RunnableConfig = invoke_kwargs.get("config") or {}
        existing_metadata: dict[str, Any] = config.get("metadata") or {}

        config["metadata"] = {
            **existing_metadata,
            FreeplayOTelAttributes.FREEPLAY_INPUT_VARIABLES.value: json.dumps(
                variables
            ),
            FreeplayOTelAttributes.FREEPLAY_PROMPT_TEMPLATE_VERSION_ID.value: prompt_info.prompt_template_version_id,
            FreeplayOTelAttributes.FREEPLAY_ENVIRONMENT.value: environment,
            FreeplayOTelAttributes.FREEPLAY_TEST_RUN_ID.value: test_run_id,
            FreeplayOTelAttributes.FREEPLAY_TEST_CASE_ID.value: test_case_id,
        }
        invoke_kwargs["config"] = config
        return invoke_kwargs

    @staticmethod
    def get_model(
        prompt_info: PromptInfo,
    ) -> Any:
        """
        Set a LangChain model for a given prompt info.

        This function checks if the required provider package is installed
        and creates the appropriate model instance.

        Args:
            prompt_info: Prompt info

        Returns:
            Instantiated LangChain model

        Raises:
            ImportError: If provider package not installed
            ValueError: If provider not supported
        """
        # Build model kwargs
        model_kwargs = {
            "model": prompt_info.model,
            **prompt_info.model_parameters,
        }

        # Try to import and instantiate based on provider
        if prompt_info.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI  # noqa: PLC0415

                return ChatOpenAI(**model_kwargs)
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-openai' package. "
                    f"Install it with: pip install langchain-openai"
                ) from e

        elif prompt_info.provider == "anthropic":
            try:
                from langchain_anthropic import ChatAnthropic  # noqa: PLC0415

                return ChatAnthropic(**model_kwargs)
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-anthropic' package. "
                    f"Install it with: pip install langchain-anthropic"
                ) from e

        elif prompt_info.provider == "vertex":
            try:
                from langchain_google_vertexai import (  # noqa: PLC0415
                    ChatVertexAI,
                )

                return ChatVertexAI(**model_kwargs)
            except ImportError as e:
                raise ImportError(
                    f"Provider '{prompt_info.provider}' requires 'langchain-google-vertexai' package. "
                    f"Install it with: pip install langchain-google-vertexai"
                ) from e

        else:
            raise ValueError(f"Unsupported provider: '{prompt_info.provider}'. ")
