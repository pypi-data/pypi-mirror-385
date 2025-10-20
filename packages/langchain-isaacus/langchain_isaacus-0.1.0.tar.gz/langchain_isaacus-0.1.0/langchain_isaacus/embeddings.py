from typing import List, Literal, Optional

from isaacus import AsyncIsaacus, Isaacus
from langchain_core.embeddings import Embeddings
from pydantic import SecretStr

_MAX_BATCH_SIZE = 128
_TASKS = {
    "query": "retrieval/query",
    "document": "retrieval/document",
}


class IsaacusEmbeddings(Embeddings):
    """Isaacus embedding model integration.

    Setup:
        Install ``langchain-isaacus`` and set environment variable ``ISAACUS_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-isaacus
            export ISAACUS_API_KEY="your-api-key"

    Key init args — completion params:
        model: str
            Name of Isaacus model to use.
        dimensions: Optional[int]
            Desired dimensionality of the embeddings. If not provided, defaults to
            the model's standard dimension. Must not be larger than the maximum
            dimension supported by the model.
        batch_size: int
            Number of texts to embed in each batch request. Default is 128.
            Should not exceed the maximum batch size supported by the model or API
            (currently 128 as of 19 October 2025).

    Key init args — client params:
        api_key: Optional[SecretStr]
            Isaacus API key. If not provided, will attempt to read from the
            ``ISAACUS_API_KEY`` environment variable.
        base_url: Optional[str]
            Base URL for the Isaacus API. Set this if you are self-hosting the Isaacus
            API as an enterprise user or are using an Isaacus API-compatible service.


    See full list of supported init args and their descriptions in the params section.

    Instantiate:
        .. code-block:: python

            from langchain_isaacus import IsaacusEmbeddings

            embed = IsaacusEmbeddings(
                model="...",
                # api_key="...", # Can provide api key directly here or set via env var.
                # dimensions=1024, # Optional, defaults to model's standard dimension.
                # base_url="https://api.isaacus.com/v1", # Only set if self-hosting.
                # batch_size=128, # Defaults to 128, the current maximum.
            )

    Embed single text:
        .. code-block:: python

            input_text = "The meaning of life is 42"
            vector = embed.embed_query(input_text)
            print(vector[:3])

        .. code-block:: python

            [-0.024603435769677162, -0.007543657906353474, 0.0039630369283258915]

    Embed multiple texts:
        .. code-block:: python

             input_texts = ["Document 1...", "Document 2..."]
            vector = embed.embed_documents(input_texts)
            print(len(vector))
            # The first 3 coordinates for the first vector
            print(vector[0][:3])

        .. code-block:: python

            [-0.024603435769677162, -0.007543657906353474, 0.0039630369283258915]

    Async:
        .. code-block:: python

            vector = await embed.aembed_query(input_text)
            print(vector[:3])

            # multiple:
            # vector = await embed.aembed_documents(input_texts)
            # print(vector[0][:3])

        .. code-block:: python

            [-0.024603435769677162, -0.007543657906353474, 0.0039630369283258915]

    """

    def __init__(
        self,
        model: str,
        api_key: Optional[SecretStr] = None,
        dimensions: Optional[int] = None,
        base_url: Optional[str] = None,
        batch_size: int = _MAX_BATCH_SIZE,
    ):
        self.model = model
        self.api_key = api_key
        self.dimensions = dimensions
        self.base_url = base_url
        self.batch_size = batch_size
        self._client = None
        self._aclient = None

    def _get_client(self) -> Isaacus:
        if not self._client:
            self._client = Isaacus(
                api_key=self.api_key,
                base_url=self.base_url,
            )

        return self._client

    def _get_aclient(self) -> AsyncIsaacus:
        if not self._aclient:
            self._aclient = AsyncIsaacus(
                api_key=self.api_key,
                base_url=self.base_url,
            )

        return self._aclient

    def _sync_embed(
        self,
        texts: List[str],
        task: Literal["query", "document"],
    ) -> List[List[float]]:
        client = self._get_client()
        task = _TASKS[task]
        embeddings: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = client.embeddings.create(
                model=self.model,
                texts=batch,
                task=task,
                dimensions=self.dimensions,
            )
            batch_embeddings = [item.embedding for item in response.embeddings]
            embeddings.extend(batch_embeddings)

        return embeddings

    async def _async_embed(
        self,
        texts: List[str],
        task: Literal["query", "document"],
    ) -> List[List[float]]:
        client = self._get_aclient()
        task = _TASKS[task]
        embeddings: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = await client.embeddings.create(
                model=self.model,
                texts=batch,
                task=task,
                dimensions=self.dimensions,
            )
            batch_embeddings = [item.embedding for item in response.embeddings]
            embeddings.extend(batch_embeddings)

        return embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        return self._sync_embed(texts, task="document")

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self._sync_embed([text], task="query")[0]

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous embed search docs."""
        return await self._async_embed(texts, task="document")

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous embed query text."""
        return (await self._async_embed([text], task="query"))[0]
