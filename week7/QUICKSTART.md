# RAG System - Quick Start Guide

Get up and running with the Document Question Answering System in 5 minutes.

---

## 🚀 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

> Note: On Windows, the project is best installed with Python 3.10 or 3.11. If you use Python 3.12, the FAISS pin is now updated, but you may still need Microsoft Visual C++ Build Tools for native dependencies such as `tokenizers`.

### Step 2: Set Your API Key
```bash
# Option A: Using environment variable (Linux/Mac)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Option B: Using .env file
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# Option C: Windows (set command)
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Run the Demo
```bash
python demo.py
```

### Step 4: Run Full Project
```bash
python rag_system.py
```

---

## 📚 What You'll Get

After running, you'll have:

1. **demo_results.json** - Answers to 4 sample questions with retrieval scores
2. **validation_report.json** - Full evaluation with all metrics
3. **metrics_report.json** - System configuration and performance stats

---

## 🎯 Quick Examples

### Example 1: Ask a Simple Question

```python
from rag_system import RAGPipeline

# Create pipeline
pipeline = RAGPipeline()

# Load a document
pipeline.setup("your_document.pdf")

# Ask a question
result = pipeline.answer_question("What is the main topic?")

# Print answer
print(result['answer'])
```

### Example 2: Batch Processing

```python
# Multiple questions
questions = [
    "What is RAG?",
    "How does retrieval work?",
    "What are the benefits?"
]

for q in questions:
    result = pipeline.answer_question(q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

### Example 3: Get System Statistics

```python
# Metrics about your system
metrics = pipeline.generate_metrics_report()

print(f"Embedding Model: {metrics['embedding_configuration']['model_name']}")
print(f"Chunks Indexed: {metrics['vector_store_configuration']['indexed_documents']}")
print(f"Vector Dimension: {metrics['embedding_configuration']['embedding_dimension']}")
```

---

## 🔧 Customization

### Use Your Own Document

```python
# PDF file
pipeline.setup("research_paper.pdf", source_type="pdf")

# Text file
pipeline.setup("notes.txt", source_type="txt")

# Raw text
pipeline.setup("""
Your document content here...
Multiple lines...
""", source_type="raw")
```

### Adjust Chunking

```python
# Change chunk size and overlap
chunking = TextChunkingModule(
    chunk_size=256,      # Smaller chunks for more specific info
    chunk_overlap=100    # More overlap for context preservation
)
```

### Retrieve More Context

```python
# Instead of default k=4, get 8 chunks
result = pipeline.answer_question("Your question", k=8)
```

---

## 🐛 Common Issues & Solutions

### Issue: "No module named 'langchain'"
```bash
pip install langchain langchain-community
```

### Issue: "API key not found"
```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY="your-key-here"
```

### Issue: "FAISS not installed"
```bash
pip install faiss-cpu
```

### Issue: Slow first run
- The first run downloads the embedding model (~100MB)
- Subsequent runs will be faster
- Use smaller embedding model if needed: `all-MiniLM-L6-v2` (faster) vs `all-mpnet-base-v2` (better)

---

## 📊 Understanding the Output

### Answer Result Structure

```python
result = {
    'query': 'Your question',
    'answer': 'The generated answer...',
    'context_chunks': [
        {
            'content': 'Chunk text...',
            'similarity_score': 0.85,
            'source': 'document.pdf',
            'chunk_id': 0
        },
        # ... more chunks
    ],
    'retrieval_scores': [0.85, 0.78, 0.72, 0.65],
    'timestamp': '2024-12-10T...'
}
```

### Interpreting Similarity Scores

| Score | Meaning |
|-------|---------|
| 0.90+ | 🟢 Highly relevant |
| 0.75-0.89 | 🟢 Very relevant |
| 0.60-0.74 | 🟡 Somewhat relevant |
| <0.60 | 🔴 May be less relevant |

---

## 🎓 Learning Path

1. **Start Here** ← You are here
2. Run `demo.py` to see it working
3. Read `README.md` for deep understanding
4. Modify `rag_system.py` to experiment
5. Implement optimizations from README
6. Build your own RAG application

---

## 📁 File Guide

| File | Purpose |
|------|---------|
| `rag_system.py` | Main implementation (1000+ lines) |
| `demo.py` | Simple demo to test the system |
| `README.md` | Comprehensive documentation |
| `QUICKSTART.md` | This file |
| `requirements.txt` | Python dependencies |
| `validation_report.json` | Test results |
| `metrics_report.json` | System metrics |

---

## 🚀 Next Steps

After the quick start:

1. **Load Your Own Document**
   ```python
   pipeline.setup("your_document.pdf")
   ```

2. **Ask Your Questions**
   ```python
   result = pipeline.answer_question("Your specific question")
   ```

3. **Generate Reports**
   ```python
   report = pipeline.generate_validation_report(["Q1", "Q2", "Q3"])
   ```

4. **Optimize**
   - Try different chunk sizes
   - Test larger embedding models
   - Implement hybrid search
   - Add re-ranking

---

## 💡 Pro Tips

### Tip 1: Cache Embeddings
```python
# Save and load vector store to avoid recomputation
import pickle
pickle.dump(pipeline.vector_db_module.vector_store, open("index.pkl", "wb"))
```

### Tip 2: Batch Processing
```python
# Process multiple documents efficiently
documents = [load(f) for f in glob.glob("*.pdf")]
for doc in documents:
    pipeline.setup(doc)
    # Query...
```

### Tip 3: Monitor Performance
```python
# Track metrics over time
metrics = pipeline.generate_metrics_report()
print(f"Retrieval accuracy: {metrics['avg_retrieval_similarity_score']}")
```

### Tip 4: Debug Retrieval
```python
# See what's being retrieved
context = pipeline.retrieval_module.retrieve(query, k=4)
for chunk in context:
    print(f"Score: {chunk['similarity_score']}")
    print(f"Content: {chunk['content'][:100]}...")
```

---

## 📞 Support

### Getting Help

1. Check `README.md` for detailed documentation
2. Review example code in `demo.py`
3. Check error messages in `validation_report.json`
4. Examine metrics in `metrics_report.json`

### Common Questions

**Q: Can I use GPT instead of Claude?**
A: Yes, modify the `AnswerGenerationModule` to use OpenAI API

**Q: How do I use GPU acceleration?**
A: Install `faiss-gpu` and use CUDA-enabled PyTorch

**Q: Can I add more documents?**
A: Yes, create a new `RAGPipeline` instance and load multiple docs

---

## ✅ Validation Checklist

- [ ] Dependencies installed
- [ ] API key configured
- [ ] `demo.py` runs successfully
- [ ] Answers make sense
- [ ] Retrieval scores are reasonable (>0.6)
- [ ] JSON reports are generated
- [ ] No errors in console output

---

## 🎉 You're Ready!

You now have a working RAG system. Start asking questions!

```bash
python demo.py
```

Happy learning! 🚀

---

**Last Updated**: December 2024  
**Status**: ✅ Ready to Use  
**Estimated Time to First Result**: 5 minutes
