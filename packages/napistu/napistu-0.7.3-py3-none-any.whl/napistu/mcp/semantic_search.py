"""
Semantic search implementation using ChromaDB for Napistu MCP server.
"""

import logging
from typing import Any, Dict, List

import chromadb
from chromadb.utils import embedding_functions

from napistu.mcp import semantic_search_utils

logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Semantic search engine using ChromaDB and sentence transformers.

    Provides AI-powered search capabilities for text content using vector embeddings.
    Manages multiple collections for different content types and handles persistent
    storage of embeddings with smart chunking for optimal search performance.

    Parameters
    ----------
    persist_directory : str, optional
        Directory path for persistent storage of ChromaDB data.
        Default is "./chroma_db". The directory will be created if it doesn't exist.
    chunk_threshold : int, optional
        Content length threshold for chunking (default 1200 chars)
    max_chunk_size : int, optional
        Maximum size per chunk (default 1000 chars)

    Attributes
    ----------
    client : chromadb.PersistentClient
        ChromaDB client instance for managing collections and persistence.
    embedding_function : chromadb.utils.embedding_functions.SentenceTransformerEmbeddingFunction
        Embedding function using the 'all-MiniLM-L6-v2' model for text vectorization.
    collections : Dict[str, chromadb.Collection]
        Dictionary mapping collection names to ChromaDB collection objects.
    chunk_threshold : int
        Content length threshold for chunking
    max_chunk_size : int
        Maximum size per chunk

    Examples
    --------
    Basic usage for semantic search:

    >>> search = SemanticSearch()
    >>> collection = search.get_or_create_collection("documents")
    >>> content = {"readme": {"install": "pip install package"}}
    >>> search.index_content("documents", content)
    >>> results = search.search("how to install", "documents")
    >>> print(f"Found {len(results)} results")

    Notes
    -----
    The class uses the 'all-MiniLM-L6-v2' sentence transformer model which:
    - Produces 384-dimensional embeddings
    - Is optimized for semantic similarity tasks
    - Has a good balance of speed and quality
    - Downloads automatically on first use (~90MB)

    ChromaDB stores embeddings persistently, so collections survive across
    sessions. The first indexing operation may be slower due to model download
    and embedding computation.

    Content is automatically chunked for optimal search performance:
    - Long documents (>1200 chars) are split into smaller, searchable chunks
    - Markdown headers are preserved to maintain document structure
    - Issues and PRs are kept as single units since they're typically shorter
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        chunk_threshold: int = 1200,
        max_chunk_size: int = 1000,
    ):
        """
        Initialize SemanticSearch with persistent ChromaDB storage.

        Parameters
        ----------
        persist_directory : str, optional
            Path to directory for storing ChromaDB data. Created if doesn't exist.
            Default is "./chroma_db".
        chunk_threshold : int, optional
            Content length threshold for chunking (default 1200 chars)
        max_chunk_size : int, optional
            Maximum size per chunk (default 1000 chars)

        Examples
        --------
        >>> search = SemanticSearch()  # Uses default ./chroma_db
        >>> search = SemanticSearch("/custom/path/db", chunk_threshold=800)  # Custom settings
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        self.collections = {}
        self.chunk_threshold = chunk_threshold
        self.max_chunk_size = max_chunk_size

    def get_or_create_collection(self, name: str):
        """
        Get existing collection or create a new one with consistent configuration.

        Parameters
        ----------
        name : str
            Name of the collection. Will be prefixed with "napistu_" for namespacing.

        Returns
        -------
        chromadb.Collection
            ChromaDB collection object for storing and querying embeddings.

        Examples
        --------
        >>> search = SemanticSearch()
        >>> collection = search.get_or_create_collection("documentation")
        >>> print(collection.name)  # "napistu_documentation"

        Notes
        -----
        Collections are cached in self.collections for efficient reuse.
        If a collection already exists, it will be loaded with the same
        embedding function to ensure consistency.
        """
        collection_name = f"napistu_{name}"

        try:
            collection = self.client.get_collection(
                name=collection_name, embedding_function=self.embedding_function
            )
        except Exception:
            # Collection doesn't exist, create it
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )

        self.collections[name] = collection
        return collection

    def index_content(self, collection_name: str, content_dict: Dict[str, Any]):
        """
        Index content into a collection for semantic search with smart chunking.

        Processes nested content dictionaries and creates searchable embeddings using
        specialized handling for different content types. Long content is automatically
        chunked for optimal search performance while preserving document structure.

        Parameters
        ----------
        collection_name : str
            Name of the collection to index content into.
        content_dict : Dict[str, Any]
            Nested dictionary containing content to index. Structure should be:
            {content_type: {name: content_text, ...}, ...}

            Special handling for content types:
            - 'issues', 'prs': Expected to contain lists of dictionaries with 'title', 'body', 'number'
            - 'wiki', 'readme': Automatically chunked if content exceeds chunk_threshold
            - Other types: Indexed as-is if content meets minimum length requirements

        Examples
        --------
        Index documentation content with mixed types:

        >>> content = {
        ...     "readme": {
        ...         "install": "Very long installation guide..." * 100,  # Will be chunked
        ...         "quickstart": "Short guide"  # Will not be chunked
        ...     },
        ...     "wiki": {
        ...         "api-reference": "## Overview\nDetailed API docs..." * 50  # Chunked by headers
        ...     },
        ...     "issues": {
        ...         "repo1": [
        ...             {"title": "Bug report", "body": "Description...", "number": 123}
        ...         ]
        ...     }
        ... }
        >>> search.index_content("documentation", content)

        Notes
        -----
        Content processing rules:
        - Issues/PRs: Combine title and body, filter content < 20 chars
        - Wiki/README: Smart chunking for content > chunk_threshold chars
        - Other content: Index as-is if > 50 chars

        Chunking preserves:
        - Markdown header structure
        - Paragraph boundaries
        - Sentence boundaries for very long paragraphs

        Each chunk gets metadata including:
        - type: Content type (wiki, readme, issues, etc.)
        - name: Original content name
        - source: Human-readable source description
        - chunk: Chunk number (0 for non-chunked content)
        - is_chunked: Boolean indicating if content was split
        - total_chunks: Total number of chunks (for chunked content)

        The collection is cleared before indexing to ensure consistency.

        Raises
        ------
        Exception
            If ChromaDB indexing fails (e.g., invalid content format)
        """
        collection = self.get_or_create_collection(collection_name)

        all_documents = []
        all_metadatas = []
        all_ids = []

        for content_type, items in content_dict.items():
            if content_type in ["issues", "prs"]:
                # Handle issues and PRs - no chunking needed as they're typically short
                documents, metadatas, ids = (
                    semantic_search_utils.process_issues_and_prs(content_type, items)
                )

            elif content_type in ["wiki", "readme", "tutorials"]:
                # Handle content that may need chunking
                documents, metadatas, ids = (
                    semantic_search_utils.process_chunkable_content(
                        content_type, items, self.chunk_threshold, self.max_chunk_size
                    )
                )

            elif content_type in ["classes", "functions", "methods"]:
                # Handle codebase content with specialized processing
                documents, metadatas, ids = (
                    semantic_search_utils.process_codebase_content(content_type, items)
                )

            else:
                logger.warning(
                    f"Unknown content type: {content_type} - this will be indexed but it may be pathological as whatever the content is will be turned into a string as-is"
                )
                # Handle regular content without chunking
                documents, metadatas, ids = (
                    semantic_search_utils.process_regular_content(content_type, items)
                )

            # Accumulate results
            all_documents.extend(documents)
            all_metadatas.extend(metadatas)
            all_ids.extend(ids)

        if all_documents:
            # Clear existing content and reindex
            try:
                collection.delete(where={})
            except Exception:
                # Collection might be empty or not properly initialized
                pass

            collection.add(
                documents=all_documents, metadatas=all_metadatas, ids=all_ids
            )

            logger.info(f"Indexed {len(all_documents)} items in {collection_name}")

            # Log breakdown by content type and chunking for debugging
            type_counts = {}
            chunk_counts = {}
            for metadata in all_metadatas:
                content_type = metadata["type"]
                type_counts[content_type] = type_counts.get(content_type, 0) + 1

                if metadata.get("is_chunked", False):
                    chunk_counts[content_type] = chunk_counts.get(content_type, 0) + 1

            logger.debug(f"Content type breakdown: {type_counts}")
            if chunk_counts:
                logger.debug(f"Chunked content counts: {chunk_counts}")
        else:
            logger.warning(f"No content to index in {collection_name}")

    def search(
        self, query: str, collection_name: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on a collection with similarity scores.

        Uses AI embeddings to find content semantically similar to the query,
        even if exact keywords don't match. Returns results with similarity scores
        and handles chunked content appropriately.

        Parameters
        ----------
        query : str
            Natural language search query. Can be keywords, phrases, or questions.
        collection_name : str
            Name of the collection to search in.
        n_results : int, optional
            Maximum number of results to return. Default is 5.

        Returns
        -------
        List[Dict[str, Any]]
            List of search results ordered by similarity (highest first), each containing:
            - 'content': The matched text content (may be a chunk of larger document)
            - 'metadata': Dictionary with type, name, source, chunking information
            - 'source': Human-readable source description (includes chunk info if applicable)
            - 'similarity_score': Float between 0 and 1 (1 = perfect match, 0 = no similarity)

        Examples
        --------
        Basic semantic search with chunked content:

        >>> results = search.search("how to install", "documentation")
        >>> for result in results:
        ...     score = result['similarity_score']
        ...     source = result['source']  # May include "(part 2)" for chunks
        ...     print(f"Score: {score:.3f} - {source}")

        Notes
        -----
        Similarity scores help you understand result quality:
        - 0.8-1.0: Very relevant matches
        - 0.6-0.8: Good matches
        - 0.4-0.6: Moderate relevance
        - 0.0-0.4: Low relevance (may not be useful)

        Chunked content handling:
        - Each chunk is searched independently for best precision
        - Source descriptions indicate chunk numbers (e.g., "wiki: API Guide (part 2)")
        - Multiple chunks from the same document may appear in results
        - This allows finding the most relevant section within long documents

        ChromaDB uses cosine similarity between embeddings, where:
        - 1.0 = identical semantic meaning
        - 0.0 = completely unrelated content
        """
        if collection_name not in self.collections:
            return []

        collection = self.collections[collection_name]

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        formatted_results = []
        for i in range(len(results["documents"][0])):
            # Convert distance to similarity score
            # ChromaDB returns distances, but we want similarity (higher = better)
            distance = results["distances"][0][i] if "distances" in results else 0.0

            # For cosine distance, similarity = 1 - distance
            similarity_score = 1.0 - distance

            formatted_results.append(
                {
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "source": results["metadatas"][0][i].get("source", "Unknown"),
                    "similarity_score": similarity_score,
                }
            )

        return formatted_results
