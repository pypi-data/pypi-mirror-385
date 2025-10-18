import logging
from typing import Optional

from notdiamond import settings
from notdiamond.exceptions import (
    UnsupportedEmbeddingProvider,
    UnsupportedLLMProvider,
)

POSSIBLE_PROVIDERS = list(settings.PROVIDERS.keys())
POSSIBLE_MODELS = list(
    model
    for provider_values in settings.PROVIDERS.values()
    for values in provider_values.values()
    if isinstance(values, list)
    for model in values
)

POSSIBLE_EMBEDDING_PROVIDERS = [
    *list(settings.EMBEDDING_PROVIDERS.keys()),
    "huggingface",
]
POSSIBLE_EMBEDDING_MODELS = list(
    model
    for provider_values in settings.EMBEDDING_PROVIDERS.values()
    for values in provider_values.values()
    if isinstance(values, list)
    for model in values
)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class LLMConfig:
    """
    A NotDiamond LLM provider config (or LLMConfig) is represented by a combination of provider and model.
    Provider refers to the company of the foundational model, such as openai, anthropic, google.
    The model represents the model name as defined by the owner company, such as gpt-3.5-turbo
    Beside this you can also specify the API key for each provider, specify extra arguments
    that are also supported by Langchain (eg. temperature), and a system prmopt to be used
    with the provider. If the provider is selected during routing, then the system prompt will
    be used, replacing the one in the message array if there are any.

    All supported providers and models can be found in our docs.

    If the API key it's not specified, it will try to pick it up from an .env file before failing.
    As example for OpenAI it will look for OPENAI_API_KEY.

    Attributes:
        provider (str): The name of the LLM provider (e.g., "openai", "anthropic"). Must be one of the
                        predefined providers in `POSSIBLE_PROVIDERS`.
        model (str): The name of the LLM model to use (e.g., "gpt-3.5-turbo").
                        Must be one of the predefined models in `POSSIBLE_MODELS`.
        system_prompt (Optional[str], optional): The system prompt to use for the provider. Defaults to None.
        api_key (Optional[str], optional): The API key for accessing the LLM provider's services.
                                            Defaults to None, in which case it tries to fetch from the settings.
        openrouter_model (str): The OpenRouter model equivalent for this provider / model
        **kwargs: Additional keyword arguments that might be necessary for specific providers or models.

    Raises:
        UnsupportedLLMProvider: If the `provider` or `model` specified is not supported.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        is_custom: bool = False,
        system_prompt: Optional[str] = None,
        context_length: Optional[int] = None,
        input_price: Optional[float] = None,
        custom_input_price: Optional[float] = None,
        output_price: Optional[float] = None,
        custom_output_price: Optional[float] = None,
        latency: Optional[float] = None,
        custom_latency: Optional[float] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """_summary_

        Args:
            provider (str): The name of the LLM provider (e.g., "openai", "anthropic").
            model (str): The name of the LLM model to use (e.g., "gpt-3.5-turbo").
            is_custom (bool): Whether this is a custom model. Defaults to False.
            system_prompt (Optional[str], optional): The system prompt to use for the provider. Defaults to None.
            context_length (Optional[int], optional): Custom context window length for the provider/model.
            custom_input_price (Optional[float], optional): Custom input price (USD) per million tokens for this
                provider/model; will default to public input price if available.
            custom_output_price (Optional[float], optional): Custom output price (USD) per million tokens for this
                provider/model; will default to public output price if available.
            custom_latency (Optional[float], optional): Custom latency (time to first token) for provider/model.
            api_key (Optional[str], optional): The API key for accessing the LLM provider's services.
                                                Defaults to None.
            **kwargs: Additional keyword arguments that might be necessary for specific providers or models.

        Raises:
            UnsupportedLLMProvider: If the `provider` or `model` specified is not supported.
        """
        if is_custom:
            self._openrouter_model = None
            self.api_key = api_key
            self.default_input_price = custom_input_price or input_price
            self.default_output_price = custom_output_price or output_price
        else:
            if provider not in POSSIBLE_PROVIDERS:
                raise UnsupportedLLMProvider(
                    f"Given LLM provider {provider} is not in the list of supported providers."
                )
            if model not in POSSIBLE_MODELS:
                raise UnsupportedLLMProvider(
                    f"Given LLM model {model} is not in the list of supported models."
                )
            self._openrouter_model = settings.PROVIDERS[provider][
                "openrouter_identifier"
            ].get(model, None)

            self.api_key = (
                api_key
                if api_key is not None
                else settings.PROVIDERS[provider]["api_key"]
            )

            self.default_input_price = settings.PROVIDERS[provider]["price"][
                model
            ]["input"]
            self.default_output_price = settings.PROVIDERS[provider]["price"][
                model
            ]["output"]

        self.provider = provider
        self.model = model
        self.system_prompt = system_prompt

        self.is_custom = is_custom
        self.context_length = context_length
        self.input_price = custom_input_price or input_price
        self.output_price = custom_output_price or output_price
        self.latency = custom_latency or latency

        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"{self.provider}/{self.model}"

    def __repr__(self) -> str:
        return f"LLMConfig({self.provider}/{self.model})"

    def __eq__(self, other):
        if isinstance(other, LLMConfig):
            return (
                self.provider == other.provider and self.model == other.model
            )
        return False

    def __hash__(self):
        return hash(str(self))

    @property
    def openrouter_model(self):
        if self._openrouter_model is None:
            LOGGER.warning(
                f"Configured model {str(self)} is not available via OpenRouter. Please try another model."
            )
        return self._openrouter_model

    def prepare_for_request(self):
        """
        Converts the LLMConfig object to a dict in the format accepted by
        the NotDiamond API.

        Returns:
            dict
        """
        return {
            "provider": self.provider,
            "model": self.model,
            "is_custom": self.is_custom,
            "context_length": self.context_length,
            "input_price": self.input_price,
            "output_price": self.output_price,
            "latency": self.latency,
        }

    def set_api_key(self, api_key: str) -> "LLMConfig":
        self.api_key = api_key

        return self

    @classmethod
    def from_string(cls, llm_provider: str):
        """
        We allow our users to specify LLM providers for NotDiamond in the string format 'provider_name/model_name',
        as example 'openai/gpt-3.5-turbo'. Underlying our workflows we want to ensure we use LLMConfig as
        the base type, so this class method converts a string specification of an LLM provider into an
        LLMConfig object.

        Args:
            llm_provider (str): this is the string definition of the LLM provider

        Returns:
            LLMConfig: initialized object with correct provider and model
        """
        split_items = llm_provider.split("/")
        if len(split_items) not in [2, 3]:
            raise ValueError(
                f"Expected string of format 'provider/model' or 'prefix/provider/model' but got {llm_provider}"
            )
        elif len(split_items) == 3:
            _, provider, model = split_items
        else:
            provider = split_items[0]
            model = split_items[1]
        return cls(provider=provider, model=model)


class EmbeddingConfig:
    """
    A NotDiamond embedding provider config (or EmbeddingConfig) is represented by a combination of provider and model.
    Provider refers to the company of the foundational model, such as openai, anthropic, google.
    The model represents the model name as defined by the owner company, such as text-embedding-3-large
    Beside this you can also specify the API key for each provider or extra arguments
    that are also supported by Langchain.

    All supported providers and models can be found in our docs.

    If the API key is not specified, the Config will try to read the key from an .env file before failing.
    For example, the Config will look for `OPENAI_API_KEY` to authenticate any OpenAI provider.

    Attributes:
        provider (str): The name of the LLM provider (e.g., "openai", "anthropic"). Must be one of the
                        predefined providers in `POSSIBLE_EMBEDDING_PROVIDERS`.
        model (str): The name of the LLM model to use (e.g., "gpt-3.5-turbo").
                        Must be one of the predefined models in `POSSIBLE_MODELS`.
        api_key (Optional[str], optional): The API key for accessing the LLM provider's services.
                                            Defaults to None, in which case it tries to fetch from the environment.
        **kwargs: Additional keyword arguments that might be necessary for specific providers or models.

    Raises:
        UnsupportedLLMProvider: If the `provider` or `model` specified is not supported.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        **kwargs,
    ):
        """_summary_

        Args:
            provider (str): The name of the embedding provider (e.g., "openai", "anthropic").
            model (str): The name of the embedding model to use (e.g., "text-embedding-3-large").
            api_key (Optional[str], optional): The API key for accessing the embedding provider's services.
                                                Defaults to None.
            **kwargs: Additional keyword arguments that might be necessary for specific providers or models.

        Raises:
            UnsupportedEmbeddingProvider: If the `provider` or `model` specified is not supported.
        """
        if provider not in POSSIBLE_EMBEDDING_PROVIDERS:
            raise UnsupportedEmbeddingProvider(
                f"Given embedding provider {provider} is not in the list of supported providers."
            )

        if (
            model not in POSSIBLE_EMBEDDING_MODELS
            and provider != "huggingface"
        ):
            raise UnsupportedEmbeddingProvider(
                f"Given embedding model {model} is not in the list of supported models."
            )

        self.api_key = (
            api_key
            if api_key is not None
            else settings.PROVIDERS[provider]["api_key"]
        )

        self.provider = provider
        self.model = model
        self.kwargs = kwargs

    def __str__(self) -> str:
        return f"{self.provider}/{self.model}"

    def __repr__(self) -> str:
        return f"EmbeddingConfig({self.provider}/{self.model})"

    def __eq__(self, other):
        if isinstance(other, EmbeddingConfig):
            return (
                self.provider == other.provider and self.model == other.model
            )
        return False

    def __hash__(self):
        return hash(str(self))

    def set_api_key(self, api_key: str) -> "EmbeddingConfig":
        self.api_key = api_key

        return self

    @classmethod
    def from_string(cls, llm_provider: str):
        """
        We allow our users to specify LLM providers for NotDiamond in the string format 'provider_name/model_name',
        for example 'openai/gpt-3.5-turbo'. Our workflows expect LLMConfig as
        the base type, so this class method converts a string specification of an LLM provider into an
        LLMConfig object.

        Args:
            llm_provider (str): this is the string definition of the LLM provider

        Returns:
            LLMConfig: initialized object with correct provider and model
        """
        split_items = llm_provider.split("/")
        if len(split_items) not in [2, 3]:
            raise ValueError(
                f"Expected string of format 'provider/model' or 'prefix/provider/model' but got {llm_provider}"
            )
        elif len(split_items) == 3:
            _, provider, model = split_items
        else:
            provider = split_items[0]
            model = split_items[1]
        return cls(provider=provider, model=model)
