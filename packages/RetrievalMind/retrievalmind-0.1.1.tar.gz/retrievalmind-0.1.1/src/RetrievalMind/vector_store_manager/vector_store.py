import os
import uuid
import numpy as np
import chromadb


class VectorStore:
    """
    Manages document embeddings in a ChromaDB vector store.

    This class provides functionality for:
      - Initializing a persistent ChromaDB client
      - Creating or loading a collection
      - Adding new documents and their embeddings to the store

    Attributes:
        collection_name (str): Name of the ChromaDB collection.
        persist_directory (str): Directory path to persist the vector store.
        document_type (str): Type of documents being stored (e.g., "PDF", "Text").
        client (chromadb.PersistentClient): Persistent ChromaDB client instance.
        collection (chromadb.Collection): The specific ChromaDB collection instance.
    """

    def __init__(self, collection_name: str, persist_directory: str, document_type: str):
        """
        Initializes the VectorStore and sets up the ChromaDB client and collection.

        Args:
            collection_name (str): Name of the collection in ChromaDB.
            persist_directory (str): Directory where the ChromaDB data will be stored.
            document_type (str): Type of documents being stored (used in metadata).

        Raises:
            RuntimeError: If ChromaDB initialization fails.
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.document_type = document_type
        self.client = None
        self.collection = None

        self._initialize_store()

    def _initialize_store(self):
        """
        Initializes the ChromaDB client and collection.

        Creates the persistence directory if it doesn't exist, and sets up
        a ChromaDB collection for storing document embeddings.

        Raises:
            RuntimeError: If the ChromaDB client or collection creation fails.
        """
        try:
            # Ensure persistence directory exists
            os.makedirs(self.persist_directory, exist_ok=True)

            # Initialize persistent ChromaDB client
            self.client = chromadb.PersistentClient(path=self.persist_directory)

            # Create or load an existing collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": f"{self.document_type} document embeddings for RAG pipeline"}
            )

            print(f"[INFO] Vector store ready: '{self.collection_name}'")
            print(f"[INFO] Current document count: {self.collection.count()}")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize vector store: {e}")

    def add_document(self, documents: list, embeddings: np.ndarray):
        """
        Adds documents and their corresponding embeddings to the ChromaDB collection.

        Args:
            documents (list): A list of document objects (from LangChain loaders).
            embeddings (np.ndarray): A NumPy array of embeddings corresponding to each document.

        Raises:
            ValueError: If documents or embeddings are empty, or their counts mismatch.
            RuntimeError: If adding to the ChromaDB collection fails.
        """
        try:
            # Validate inputs
            if not documents or len(documents) == 0:
                raise ValueError("Document list cannot be empty.")
            if embeddings is None or len(embeddings) == 0:
                raise ValueError("Embeddings cannot be empty.")
            if len(documents) != len(embeddings):
                raise ValueError("Number of documents and embeddings must match.")

            ids, metadatas, documents_text, embeddings_list = [], [], [], []

            # Prepare ChromaDB records
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                doc_id = f"doc_{uuid.uuid4().hex[:8]}_{i}"
                ids.append(doc_id)

                # Convert metadata safely
                metadata = dict(getattr(doc, "metadata", {}))
                metadata.update({
                    "doc_index": i,
                    "content_length": len(getattr(doc, "page_content", "")),
                })
                metadatas.append(metadata)

                documents_text.append(getattr(doc, "page_content", ""))
                embeddings_list.append(embedding.tolist())

            # Add data to ChromaDB collection
            self.collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas,
                embeddings=embeddings_list
            )

            print(f"[INFO] Successfully added {len(documents)} documents to '{self.collection_name}'.")
            print(f"[INFO] Total documents in collection: {self.collection.count()}")

        except ValueError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Failed to add documents to vector store: {e}")