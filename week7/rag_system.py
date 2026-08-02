"""
Document Question Answering System (RAG)
Week 7 Project - Complete Implementation
Author: Asta
Date: 2026
"""

import os
import json
import time
from datetime import datetime
from typing import List, Tuple, Dict, Any
import re
from pathlib import Path

# Try importing dependencies, provide graceful fallback
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    from anthropic import Anthropic
    import PyPDF2
    DEPS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Some dependencies not installed. Provide mock implementation.")
    DEPS_AVAILABLE = False


class DocumentIngestionModule:
    """
    Handles loading and preprocessing of various document formats.
    Supports: PDF, TXT, and raw text input
    """
    
    def __init__(self):
        self.loaded_documents = []
        self.source_metadata = {}
    
    def load_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")
    
    def load_text_file(self, file_path: str) -> str:
        """Load raw text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error loading text file: {e}")
    
    def load_documents(self, source: str, source_type: str = "auto") -> List[Document]:
        """
        Load documents from various sources.
        
        Args:
            source: File path or raw text
            source_type: "pdf", "txt", "raw", or "auto"
        
        Returns:
            List of Document objects with metadata
        """
        documents = []
        
        # Auto-detect source type
        if source_type == "auto":
            if os.path.isfile(source):
                if source.lower().endswith('.pdf'):
                    source_type = "pdf"
                elif source.lower().endswith('.txt'):
                    source_type = "txt"
            else:
                source_type = "raw"
        
        # Load based on type
        if source_type == "pdf":
            text = self.load_pdf(source)
            metadata = {"source": source, "type": "pdf"}
        elif source_type == "txt":
            text = self.load_text_file(source)
            metadata = {"source": source, "type": "txt"}
        elif source_type == "raw":
            text = source
            metadata = {"source": "raw_input", "type": "text"}
        else:
            raise ValueError(f"Unknown source type: {source_type}")
        
        # Create document object
        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)
        self.loaded_documents.extend(documents)
        self.source_metadata[metadata["source"]] = metadata
        
        return documents


class TextChunkingModule:
    """
    Splits documents into manageable chunks for embedding.
    Uses recursive character splitting for optimal chunk boundaries.
    """
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize chunking module.
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.chunks = []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects
        
        Returns:
            List of chunked Document objects
        """
        self.chunks = self.splitter.split_documents(documents)
        
        # Add chunk metadata
        for i, chunk in enumerate(self.chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        return self.chunks
    
    def get_chunking_profile(self) -> Dict[str, Any]:
        """Return statistics about chunking"""
        if not self.chunks:
            return {}
        
        sizes = [len(chunk.page_content) for chunk in self.chunks]
        return {
            "total_chunks": len(self.chunks),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "avg_chunk_size": sum(sizes) / len(sizes),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
            "total_content_length": sum(sizes)
        }


class EmbeddingModule:
    """
    Converts text chunks into vector embeddings.
    Uses Sentence Transformers for semantic embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding module.
        
        Args:
            model_name: HuggingFace model for embeddings
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.embedding_dimension = None
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.embedding_dimension is None:
            sample_embedding = self.embeddings.embed_query("sample text")
            self.embedding_dimension = len(sample_embedding)
        return self.embedding_dimension


class VectorDatabaseModule:
    """
    Manages vector storage and similarity search using FAISS.
    Provides efficient nearest neighbor search over embeddings.
    """
    
    def __init__(self, embedding_module: EmbeddingModule):
        """
        Initialize vector database.
        
        Args:
            embedding_module: EmbeddingModule instance for creating vectors
        """
        self.embedding_module = embedding_module
        self.vector_store = None
        self.documents = []
    
    def build_index(self, documents: List[Document]) -> None:
        """
        Build FAISS index from documents.
        
        Args:
            documents: List of Document chunks with content
        """
        self.documents = documents
        self.vector_store = FAISS.from_documents(
            documents,
            self.embedding_module.embeddings
        )
    
    def retrieve_relevant_chunks(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """
        Retrieve most relevant chunks for a query.
        
        Args:
            query: User question or search query
            k: Number of chunks to retrieve
        
        Returns:
            List of (Document, similarity_score) tuples
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call build_index first.")
        
        # Retrieve with similarity scores
        results = self.vector_store.similarity_search_with_scores(query, k=k)
        return results
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        return {
            "indexed_documents": len(self.documents),
            "vector_store_type": "FAISS",
            "embedding_model": self.embedding_module.model_name,
            "embedding_dimension": self.embedding_module.get_embedding_dimension(),
            "index_initialized": self.vector_store is not None
        }


class QueryProcessingModule:
    """
    Processes user queries and converts them to embeddings.
    Handles query preprocessing and normalization.
    """
    
    def __init__(self, embedding_module: EmbeddingModule):
        self.embedding_module = embedding_module
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess user query.
        
        Args:
            query: Raw user input
        
        Returns:
            Cleaned query string
        """
        # Remove extra whitespace
        query = " ".join(query.split())
        # Normalize case for consistency (keep original for display)
        return query.strip()
    
    def process_query(self, query: str) -> Tuple[str, Any]:
        """
        Process user query and generate embedding.
        
        Args:
            query: User question
        
        Returns:
            Tuple of (processed_query, embedding)
        """
        processed = self.preprocess_query(query)
        embedding = self.embedding_module.embeddings.embed_query(processed)
        return processed, embedding


class RetrievalModule:
    """
    Retrieves relevant document chunks based on query similarity.
    """
    
    def __init__(self, vector_db: VectorDatabaseModule):
        self.vector_db = vector_db
        self.retrieval_log = []
    
    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User question
            k: Number of chunks to retrieve
        
        Returns:
            List of context chunks with metadata
        """
        results = self.vector_db.retrieve_relevant_chunks(query, k=k)
        
        context_chunks = []
        for doc, score in results:
            chunk_info = {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "chunk_id": doc.metadata.get("chunk_id", -1),
                "similarity_score": float(score),
                "chunk_size": len(doc.page_content)
            }
            context_chunks.append(chunk_info)
            
            # Log retrieval
            self.retrieval_log.append({
                "query": query,
                "retrieved_chunk_id": chunk_info["chunk_id"],
                "similarity_score": chunk_info["similarity_score"],
                "timestamp": datetime.now().isoformat()
            })
        
        return context_chunks


class AnswerGenerationModule:
    """
    Generates answers using Claude with retrieved context.
    Ensures answers are grounded in document content.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize answer generation module.
        
        Args:
            api_key: Anthropic API key (uses env if not provided)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key) if self.api_key else None
        self.model = "claude-opus-4-1"  # Or latest available model
        self.generation_log = []
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate answer using Claude with retrieved context.
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks
        
        Returns:
            Generated answer grounded in context
        """
        if not context_chunks:
            return "No relevant context was found for this query."

        if self.client is None:
            top_chunk = context_chunks[0]["content"]
            short_answer = re.sub(r"\s+", " ", top_chunk).strip()
            if len(short_answer) > 350:
                short_answer = short_answer[:347].rstrip() + "..."
            answer = (
                f"Based on the retrieved context, the best match suggests: {short_answer}"
            )
            self.generation_log.append({
                "query": query,
                "answer": answer,
                "context_chunks_used": len(context_chunks),
                "generation_time": 0.0,
                "timestamp": datetime.now().isoformat()
            })
            return answer

        # Build context string
        context_text = "\n\n".join([
            f"[Chunk {chunk['chunk_id']} from {chunk['source']}]\n{chunk['content']}"
            for chunk in context_chunks
        ])
        
        # Build prompt
        system_prompt = """You are a helpful assistant that answers questions based on provided documents.
Always ground your answers in the provided context. If the context doesn't contain relevant information,
explicitly state that. Be concise and accurate."""
        
        user_prompt = f"""Based on the following document excerpts, answer this question:

QUESTION: {query}

DOCUMENT CONTEXT:
{context_text}

ANSWER:"""
        
        # Generate response
        start_time = time.time()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        generation_time = time.time() - start_time
        
        answer = response.content[0].text
        
        # Log generation
        self.generation_log.append({
            "query": query,
            "answer": answer,
            "context_chunks_used": len(context_chunks),
            "generation_time": generation_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return answer


class RAGPipeline:
    """
    Complete RAG system orchestrating all components.
    """
    
    def __init__(self):
        self.ingestion_module = DocumentIngestionModule()
        self.chunking_module = TextChunkingModule(chunk_size=512, chunk_overlap=50)
        self.embedding_module = EmbeddingModule()
        self.vector_db_module = VectorDatabaseModule(self.embedding_module)
        self.query_module = QueryProcessingModule(self.embedding_module)
        self.retrieval_module = RetrievalModule(self.vector_db_module)
        self.answer_module = AnswerGenerationModule()
        
        self.documents_loaded = False
        self.index_built = False
    
    def setup(self, document_source: str, source_type: str = "auto") -> None:
        """
        Initialize RAG pipeline with documents.
        
        Args:
            document_source: File path or raw text
            source_type: Document type ("pdf", "txt", "raw", or "auto")
        """
        print("📄 Step 1: Loading documents...")
        documents = self.ingestion_module.load_documents(document_source, source_type)
        print(f"   ✓ Loaded {len(documents)} document(s)")
        
        print("\n✂️ Step 2: Chunking text...")
        chunks = self.chunking_module.chunk_documents(documents)
        profile = self.chunking_module.get_chunking_profile()
        print(f"   ✓ Created {profile['total_chunks']} chunks")
        print(f"   ✓ Avg chunk size: {profile['avg_chunk_size']:.0f} characters")
        
        print("\n🧠 Step 3: Building embeddings...")
        embedding_dim = self.embedding_module.get_embedding_dimension()
        print(f"   ✓ Embedding dimension: {embedding_dim}")
        
        print("\n📊 Step 4: Building vector database...")
        self.vector_db_module.build_index(chunks)
        db_stats = self.vector_db_module.get_db_stats()
        print(f"   ✓ Indexed {db_stats['indexed_documents']} documents")
        
        self.documents_loaded = True
        self.index_built = True
        print("\n✅ Pipeline setup complete!\n")
    
    def answer_question(self, query: str, k: int = 4) -> Dict[str, Any]:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            query: User question
            k: Number of context chunks to retrieve
        
        Returns:
            Dictionary containing question, context, and answer
        """
        if not self.index_built:
            raise ValueError("Pipeline not initialized. Call setup() first.")
        
        print(f"❓ Question: {query}\n")
        
        # Retrieve context
        print("🔍 Retrieving relevant chunks...")
        context_chunks = self.retrieval_module.retrieve(query, k=k)
        print(f"   ✓ Retrieved {len(context_chunks)} chunks\n")
        
        # Generate answer
        print("💭 Generating answer...")
        answer = self.answer_module.generate_answer(query, context_chunks)
        print(f"   ✓ Answer generated\n")
        
        result = {
            "query": query,
            "answer": answer,
            "context_chunks": context_chunks,
            "retrieval_scores": [chunk["similarity_score"] for chunk in context_chunks],
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def generate_validation_report(self, test_questions: List[str]) -> Dict[str, Any]:
        """
        Generate validation report with test results.
        
        Args:
            test_questions: List of test questions
        
        Returns:
            Validation report dictionary
        """
        print("\n" + "="*60)
        print("VALIDATION REPORT - Testing RAG System")
        print("="*60 + "\n")
        
        results = []
        for i, question in enumerate(test_questions, 1):
            print(f"Test {i}/{len(test_questions)}: {question}")
            result = self.answer_question(question)
            results.append(result)
            print(f"Answer: {result['answer'][:150]}...\n")
        
        report = {
            "test_date": datetime.now().isoformat(),
            "total_questions": len(test_questions),
            "results": results,
            "avg_retrieval_score": sum(
                sum(r["retrieval_scores"]) / len(r["retrieval_scores"])
                for r in results
            ) / len(results),
            "retrieval_logs": self.retrieval_module.retrieval_log,
            "generation_logs": self.answer_module.generation_log
        }
        
        return report
    
    def generate_metrics_report(self) -> Dict[str, Any]:
        """Generate comprehensive system metrics report"""
        return {
            "system_info": {
                "timestamp": datetime.now().isoformat(),
                "model": self.answer_module.model
            },
            "chunking_profile": self.chunking_module.get_chunking_profile(),
            "embedding_model": self.embedding_module.model_name,
            "embedding_dimension": self.embedding_module.get_embedding_dimension(),
            "vector_store_stats": self.vector_db_module.get_db_stats(),
            "document_sources": self.ingestion_module.source_metadata
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution demonstrating the RAG pipeline"""
    
    print("\n" + "="*60)
    print("DOCUMENT QUESTION ANSWERING SYSTEM (RAG)")
    print("Week 7 Project Implementation")
    print("="*60 + "\n")
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Load sample document (you can replace with your own)
    sample_document = """
    Retrieval-Augmented Generation (RAG) is a technique that combines information retrieval
    with text generation. Instead of relying solely on a language model's pre-trained knowledge,
    RAG systems retrieve relevant documents or passages and use them as context to generate
    more accurate and grounded responses.
    
    The main components of a RAG system include:
    
    1. Document Ingestion: Loading and preprocessing documents from various sources such as PDFs,
    text files, or databases. This step ensures that documents are in a format suitable for
    further processing.
    
    2. Text Chunking: Breaking large documents into smaller, overlapping chunks. This improves
    retrieval accuracy because the model can find more specific and relevant information.
    
    3. Embedding Generation: Converting text chunks into vector representations using embedding
    models. These vectors capture the semantic meaning of the text.
    
    4. Vector Database: Storing embeddings in a searchable database like FAISS, Pinecone, or
    Weaviate. This allows for efficient similarity search operations.
    
    5. Query Processing: Converting user queries into embeddings using the same embedding model
    used for documents. This ensures compatibility for similarity matching.
    
    6. Retrieval: Searching the vector database to find the most similar chunks relative to
    the user's query. Common similarity measures include cosine similarity and Euclidean distance.
    
    7. Generation: Using a language model (like Claude or GPT) to generate answers based on
    both the user's query and the retrieved context. This grounding ensures factually accurate
    responses.
    
    Benefits of RAG:
    - Improved accuracy through grounding in real documents
    - Ability to work with private or domain-specific data
    - Reduced hallucinations compared to pure language models
    - Support for knowledge updates without retraining
    - Better performance on factual questions
    
    Applications:
    - Enterprise search systems
    - Customer support chatbots
    - Knowledge assistants
    - Research paper analysis
    - Documentation tools
    - Recommendation systems
    
    The effectiveness of a RAG system depends on:
    1. Quality of document chunks and embeddings
    2. Relevance of retrieved context
    3. Quality of the underlying language model
    4. Prompt engineering for answer generation
    
    Future improvements include hybrid search combining keyword and semantic search,
    re-ranking models for better relevance, and multi-hop reasoning over multiple documents.
    """
    
    # Setup pipeline
    pipeline.setup(sample_document, source_type="raw")
    
    # Test questions
    test_questions = [
        "What are the main components of a RAG system?",
        "How does text chunking improve RAG performance?",
        "What are the benefits of using RAG?",
        "Name some applications of RAG systems."
    ]
    
    # Generate validation report
    validation_report = pipeline.generate_validation_report(test_questions)
    
    # Generate metrics report
    metrics_report = pipeline.generate_metrics_report()
    
    # Save reports
    with open("/home/claude/validation_report.json", "w") as f:
        json.dump(validation_report, f, indent=2, default=str)
    
    with open("/home/claude/metrics_report.json", "w") as f:
        json.dump(metrics_report, f, indent=2, default=str)
    
    print("="*60)
    print("✅ Reports generated:")
    print("   - validation_report.json")
    print("   - metrics_report.json")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
