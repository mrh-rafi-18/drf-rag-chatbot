from langchain_chroma import Chroma  # updated
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
import os, shutil, logging
from typing import List, Optional
from django.conf import settings





logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
VECTOR_STORE_BASE_DIR = settings.VECTOR_STORE_BASE_DIR
COLLECTION_NAME_TEMPLATE = "user_{user_id}_docs"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
RETRIEVER_K = 5
LLM_MAX_NEW_TOKENS = 200
LLM_TEMPERATURE = 0.5


class RAGPipeline:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.collection_name = COLLECTION_NAME_TEMPLATE.format(user_id=user_id)
        self.persist_dir = os.path.join(VECTOR_STORE_BASE_DIR, f"user_{user_id}")
        os.makedirs(self.persist_dir, exist_ok=True)

        self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

        # Vector store
        self.vector_store: Optional[Chroma] = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir
        )

        # LLM and Chat
        self.llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            task="text-generation",
            max_new_tokens=LLM_MAX_NEW_TOKENS,
            temperature=LLM_TEMPERATURE
        )
        self.chat_model = ChatHuggingFace(llm=self.llm)

    def _load_documents(self, file_path: str) -> List:
        ext = os.path.splitext(file_path)[1].lower()
        loaders = {".pdf": PyPDFLoader, ".docx": Docx2txtLoader, ".txt": TextLoader}
        loader_class = loaders.get(ext)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {ext}")
        return loader_class(file_path).load()

    def _split_documents(self, documents: List):
        splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        return splitter.split_documents(documents)

    def process_document(self, file_path: str, doc_id: Optional[int] = None):
        try:
            docs = self._load_documents(file_path)
            chunks = self._split_documents(docs)
            if doc_id:
                for chunk in chunks:
                    chunk.metadata['doc_id'] = doc_id
            self.vector_store.add_documents(chunks)
            logger.info(f"Added {len(chunks)} chunks from {file_path}")
            return len(chunks)
        except Exception as e:
            logger.error(f"Failed to add document {file_path}: {e}")
            return 0


    def get_retriever(self):
        return self.vector_store.as_retriever(search_type="similarity", search_kwargs={"k": RETRIEVER_K})

    def query(self, question: str, chat_history: Optional[List] = None):
        try:
            retriever = self.get_retriever()
            docs = retriever.invoke(question)
            if not docs:
                return {"answer": "No relevant documents found.", "sources": []}
            context = "\n\n".join([doc.page_content for doc in docs])
            prompt = PromptTemplate(
                template="""You are a helpful assistant answering questions based on user's documents.

Context:
{context}

Question: {question}

Answer:""",
                input_variables=["context", "question"]
            )
            answer = self.chat_model.invoke(prompt.format(context=context, question=question)).content
            sources, seen = [], set()
            for doc in docs:
                src_file = os.path.basename(doc.metadata.get("source", "Unknown"))
                if src_file not in seen:
                    sources.append({"title": src_file, "type": "personal_document"})
                    seen.add(src_file)
            return {"answer": answer, "sources": sources}
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {"answer": "Error during query.", "sources": []}

    def delete_document(self, doc_id: int) -> bool:
        try:
            collection = self.vector_store._collection
            result = collection.get(where={"doc_id": doc_id})
            if result and result["ids"]:
                collection.delete(ids=result["ids"])
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def clear_all(self) -> bool:
        try:
            self.vector_store.delete_collection()
            if os.path.exists(self.persist_dir):
                shutil.rmtree(self.persist_dir)
            return True
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            return False

    def get_document_count(self) -> int:
        try:
            return self.vector_store._collection.count()
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
