import asyncio
import logging
from typing import Any, AsyncGenerator

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock, BedrockEmbeddings
from langchain_ibm import ChatWatsonx, WatsonxEmbeddings
from langchain_perplexity import ChatPerplexity
from langchain_core.runnables import Runnable

logger = logging.getLogger("CustomLangchainClient")


class CustomLangchainClient(Runnable):
    """
    Unified LangChain client that receives the provider and creates the appropriate model.
    """

    def __init__(self, provider: str, **kwargs):
        """
        Args:
            provider: string indicating the provider ("openai", "anthropic", "bedrock"...)
            kwargs: extra arguments (like api_key, model, etc.)
        """
        self.provider = provider.lower()
        self.kwargs = kwargs
        self.model = self._init_model()

    def __getattr__(self, name):
        """
        Delegate unknown attribute/method access to the underlying LangChain model.
        """
        return getattr(self.model, name)

    def _init_model(self):
        if self.provider == "openai":
            return ChatOpenAI(**self.kwargs)
        elif self.provider == "anthropic":
            return ChatAnthropic(**self.kwargs)
        elif self.provider == "bedrock":
            return ChatBedrock(**self.kwargs)
        elif self.provider == "watsonx":
            return ChatWatsonx(**self.kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")


    def invoke(self, messages: list, config=None, **kwargs):
        """
        Executes text generation with LangChain (compatible with Runnable.invoke).
        """
        try:
            if isinstance(messages, dict) and "input" in messages:
                messages = messages["input"]

            response = self.model.invoke(messages, **kwargs)

            setattr(response, "flashquery", {})

            return response

        except Exception as ex:
            logger.error(f"Error generating response with {self.provider}: {ex}")
            raise


    async def astream(self, input: Any, config: dict | None = None, **kwargs) -> AsyncGenerator[Any, None]:
        """
        Async streaming with .flashquery in each chunk.
        """
        async for chunk in self.model.astream(input, config=config, **kwargs):
            setattr(chunk, "flashquery", {})
            yield chunk


    async def ainvoke(self, input: Any, config: dict | None = None, **kwargs):
        """
        Single async call (no streaming).
        """
        try:
            response = await self.model.ainvoke(input, config=config, **kwargs)
            setattr(response, "flashquery", {})
            return response
        except Exception as ex:
            logger.error(f"Error in ainvoke with {self.provider}: {ex}")
            raise
    
    def bind(self, **new_kwargs):
        """
        Returns a new instance of CustomLangchainClient with updated parameters.
        Works like LangChain's .bind() to pre-configure parameters.
        """
        try:
            # Merge existing kwargs with new ones
            updated_kwargs = {**self.kwargs, **new_kwargs}
            return CustomLangchainClient(self.provider, **updated_kwargs)
        except Exception as ex:
            logger.error(f"Error binding model for {self.provider}: {ex}")
            raise


class CustomEmbeddingsClient(Runnable):
    """
    Unified LangChain client for embeddings models (OpenAI, Bedrock, Watsonx).
    """

    def __init__(self, provider: str, **kwargs):
        self.provider = provider.lower()
        self.kwargs = kwargs
        self.model = self._init_model()

    def __getattr__(self, name):
        """
        Delegate unknown attribute/method access to the underlying LangChain model.
        """
        return getattr(self.model, name)

    def _init_model(self):
        if self.provider == "openai":
            return OpenAIEmbeddings(**self.kwargs)
        elif self.provider == "bedrock":
            return BedrockEmbeddings(**self.kwargs)
        elif self.provider == "watsonx":
            return WatsonxEmbeddings(**self.kwargs)
        elif self.provider == "perplexity":
            return ChatPerplexity(**self.kwargs)
        else:
            raise ValueError(
                f"Unsupported embeddings provider: {self.provider}")

    def embed_documents(self, documents: list[str], **kwargs):
        try:
            return self.model.embed_documents(documents, **kwargs)
        except Exception as ex:
            logger.error(
                f"Error embedding documents with {self.provider}: {ex}")
            raise

    def embed_query(self, query: str, **kwargs):
        try:
            return self.model.embed_query(query, **kwargs)
        except Exception as ex:
            logger.error(f"Error embedding query with {self.provider}: {ex}")
            raise

    async def aembed_documents(self, documents: list[str], **kwargs):
        try:
            return await asyncio.to_thread(
                self.model.embed_documents, documents, **kwargs
            )
        except Exception as ex:
            logger.error(
                f"Async error embedding documents with {self.provider}: {ex}")
            raise

    async def aembed_query(self, query: str, **kwargs):
        try:
            return await asyncio.to_thread(
                self.model.embed_query, query, **kwargs
            )
        except Exception as ex:
            logger.error(
                f"Async error embedding query with {self.provider}: {ex}")
            raise