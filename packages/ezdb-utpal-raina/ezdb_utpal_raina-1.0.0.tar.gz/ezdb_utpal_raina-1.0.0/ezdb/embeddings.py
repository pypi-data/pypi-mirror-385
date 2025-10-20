"""
Embedding models for automatic text-to-vector conversion.
"""
from typing import List, Union, Optional
import numpy as np
from abc import ABC, abstractmethod


class EmbeddingFunction(ABC):
    """Base class for embedding functions."""

    @abstractmethod
    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Convert text(s) to vector embeddings.

        Args:
            texts: Single text string or list of texts

        Returns:
            numpy array of shape (n_texts, dimension)
        """
        pass

    @abstractmethod
    def dimension(self) -> int:
        """Return the dimension of embeddings produced by this function."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of this embedding function."""
        pass


class SentenceTransformerEmbedding(EmbeddingFunction):
    """
    Sentence-BERT embedding function using sentence-transformers library.
    Free, runs locally, no API key needed.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Sentence-BERT embedding function.

        Args:
            model_name: Name of the sentence-transformers model
                       Default: 'all-MiniLM-L6-v2' (384 dimensions)
                       Other options:
                       - 'all-mpnet-base-v2' (768 dimensions, better quality)
                       - 'paraphrase-multilingual-MiniLM-L12-v2' (384 dims, multilingual)
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for SentenceTransformerEmbedding. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Convert text(s) to embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings

    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def name(self) -> str:
        """Return model name."""
        return f"sentence-transformers/{self.model_name}"


class OpenAIEmbedding(EmbeddingFunction):
    """
    OpenAI embedding function using OpenAI API.
    Requires API key and internet connection. Paid service.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-3-small"
    ):
        """
        Initialize OpenAI embedding function.

        Args:
            api_key: OpenAI API key
            model_name: OpenAI embedding model name
                       Options:
                       - 'text-embedding-3-small' (1536 dims, $0.02/1M tokens)
                       - 'text-embedding-3-large' (3072 dims, $0.13/1M tokens)
                       - 'text-embedding-ada-002' (1536 dims, legacy)
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai is required for OpenAIEmbedding. "
                "Install with: pip install openai"
            )

        self.model_name = model_name
        self.client = OpenAI(api_key=api_key)

        # Dimension mapping
        self._dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        self._dimension = self._dimension_map.get(model_name, 1536)

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Convert text(s) to embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )

        embeddings = [data.embedding for data in response.data]
        return np.array(embeddings)

    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def name(self) -> str:
        """Return model name."""
        return f"openai/{self.model_name}"


class CohereEmbedding(EmbeddingFunction):
    """
    Cohere embedding function using Cohere API.
    Requires API key and internet connection. Paid service.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "embed-english-v3.0"
    ):
        """
        Initialize Cohere embedding function.

        Args:
            api_key: Cohere API key
            model_name: Cohere embedding model name
                       Options:
                       - 'embed-english-v3.0' (1024 dims)
                       - 'embed-multilingual-v3.0' (1024 dims)
                       - 'embed-english-light-v3.0' (384 dims)
        """
        try:
            import cohere
        except ImportError:
            raise ImportError(
                "cohere is required for CohereEmbedding. "
                "Install with: pip install cohere"
            )

        self.model_name = model_name
        self.client = cohere.Client(api_key=api_key)

        # Dimension mapping
        self._dimension_map = {
            "embed-english-v3.0": 1024,
            "embed-multilingual-v3.0": 1024,
            "embed-english-light-v3.0": 384,
        }
        self._dimension = self._dimension_map.get(model_name, 1024)

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Convert text(s) to embeddings."""
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embed(
            texts=texts,
            model=self.model_name,
            input_type="search_document"
        )

        return np.array(response.embeddings)

    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def name(self) -> str:
        """Return model name."""
        return f"cohere/{self.model_name}"


class HuggingFaceEmbedding(EmbeddingFunction):
    """
    HuggingFace Transformers embedding function.
    Free, runs locally, highly customizable.
    """

    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize HuggingFace embedding function.

        Args:
            model_name: HuggingFace model name
                       Examples:
                       - 'bert-base-uncased' (768 dims)
                       - 'distilbert-base-uncased' (768 dims, faster)
                       - 'roberta-base' (768 dims)
        """
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch
        except ImportError:
            raise ImportError(
                "transformers and torch are required for HuggingFaceEmbedding. "
                "Install with: pip install transformers torch"
            )

        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

        # Get dimension from model config
        self._dimension = self.model.config.hidden_size

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Convert text(s) to embeddings."""
        import torch

        if isinstance(texts, str):
            texts = [texts]

        # Tokenize
        inputs = self.tokenizer(
            texts,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()

    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def name(self) -> str:
        """Return model name."""
        return f"huggingface/{self.model_name}"


# Convenience factory function
def create_embedding_function(
    provider: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
) -> EmbeddingFunction:
    """
    Factory function to create embedding functions.

    Args:
        provider: Embedding provider ('sentence-transformers', 'openai', 'cohere', 'huggingface')
        model_name: Optional model name (uses default if not provided)
        api_key: API key for cloud providers (OpenAI, Cohere)

    Returns:
        EmbeddingFunction instance

    Examples:
        >>> # Free, local Sentence-BERT
        >>> embedding_fn = create_embedding_function('sentence-transformers')
        >>>
        >>> # OpenAI with custom model
        >>> embedding_fn = create_embedding_function(
        ...     'openai',
        ...     model_name='text-embedding-3-large',
        ...     api_key='sk-...'
        ... )
    """
    provider = provider.lower()

    if provider in ['sentence-transformers', 'sbert', 'sentence-bert']:
        model = model_name or 'all-MiniLM-L6-v2'
        return SentenceTransformerEmbedding(model)

    elif provider == 'openai':
        if not api_key:
            raise ValueError("api_key is required for OpenAI embeddings")
        model = model_name or 'text-embedding-3-small'
        return OpenAIEmbedding(api_key, model)

    elif provider == 'cohere':
        if not api_key:
            raise ValueError("api_key is required for Cohere embeddings")
        model = model_name or 'embed-english-v3.0'
        return CohereEmbedding(api_key, model)

    elif provider in ['huggingface', 'transformers']:
        model = model_name or 'bert-base-uncased'
        return HuggingFaceEmbedding(model)

    elif provider in ['clip', 'multimodal']:
        model = model_name or 'clip-ViT-B-32'
        return CLIPEmbedding(model)

    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported: sentence-transformers, openai, cohere, huggingface, clip"
        )


class CLIPEmbedding(EmbeddingFunction):
    """
    CLIP multimodal embedding function for both text and images.
    Uses OpenAI's CLIP model via sentence-transformers.
    Free, runs locally, supports text and images in same vector space.
    """

    def __init__(self, model_name: str = "clip-ViT-B-32"):
        """
        Initialize CLIP embedding function.

        Args:
            model_name: CLIP model variant
                       Options:
                       - 'clip-ViT-B-32' (512 dims, fastest)
                       - 'clip-ViT-B-16' (512 dims, better quality)
                       - 'clip-ViT-L-14' (768 dims, best quality, slower)
        """
        try:
            from sentence_transformers import SentenceTransformer
            from PIL import Image
            import io
            import base64
        except ImportError:
            raise ImportError(
                "sentence-transformers and Pillow are required for CLIP. "
                "Install with: pip install sentence-transformers pillow"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        # For CLIP models, get_sentence_embedding_dimension() may return None
        self._dimension = self.model.get_sentence_embedding_dimension()
        if self._dimension is None:
            # Fallback: encode a dummy text to get dimension
            dummy_embedding = self.model.encode(["test"], convert_to_numpy=True)
            self._dimension = dummy_embedding.shape[1]

    def embed(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Convert text(s) to embeddings.

        Note: For images, use embed_images() method instead.
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings

    def embed_images(self, images: Union[str, List[str]]) -> np.ndarray:
        """
        Convert image(s) to embeddings.

        Args:
            images: Single image or list of images
                   Can be:
                   - File path: '/path/to/image.jpg'
                   - URL: 'http://example.com/image.jpg'
                   - Base64: 'data:image/jpeg;base64,/9j/4AAQ...'

        Returns:
            numpy array of shape (n_images, dimension)
        """
        from PIL import Image
        import io
        import base64
        import requests

        if isinstance(images, str):
            images = [images]

        pil_images = []
        for img in images:
            if img.startswith('data:image'):
                # Base64 encoded image
                header, encoded = img.split(',', 1)
                image_data = base64.b64decode(encoded)
                pil_img = Image.open(io.BytesIO(image_data))
            elif img.startswith('http://') or img.startswith('https://'):
                # URL
                response = requests.get(img)
                pil_img = Image.open(io.BytesIO(response.content))
            else:
                # File path
                pil_img = Image.open(img)

            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')

            pil_images.append(pil_img)

        # Encode images
        embeddings = self.model.encode(pil_images, convert_to_numpy=True)
        return embeddings

    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    def name(self) -> str:
        """Return model name."""
        return f"clip/{self.model_name}"


# Default embedding function (free, no setup required)
def default_embedding_function() -> EmbeddingFunction:
    """
    Create default embedding function (Sentence-BERT with all-MiniLM-L6-v2).
    This is free and runs locally without any API keys.
    """
    return SentenceTransformerEmbedding('all-MiniLM-L6-v2')
