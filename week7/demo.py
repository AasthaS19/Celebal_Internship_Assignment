"""
RAG System - Quick Demo
Week 7 Project - Simple Usage Example
"""

from pathlib import Path
from rag_system import RAGPipeline
import json

def main():
    """Demonstrate the RAG system"""
    
    print("\n" + "="*70)
    print(" RAG SYSTEM - QUICK DEMO")
    print("="*70)
    
    # Example document - Machine Learning Basics
    ml_document = """
    Machine Learning Fundamentals
    
    Machine Learning (ML) is a subset of artificial intelligence that enables
    systems to learn and improve from experience without being explicitly programmed.
    
    Types of Machine Learning:
    
    1. Supervised Learning
    Supervised learning involves training on labeled data where the output is known.
    Common algorithms include:
    - Linear Regression: For continuous predictions
    - Logistic Regression: For binary classification
    - Decision Trees: For non-linear relationships
    - Support Vector Machines: For complex boundaries
    - Neural Networks: For deep learning tasks
    
    2. Unsupervised Learning
    Unsupervised learning finds patterns in unlabeled data.
    Key techniques:
    - Clustering: Groups similar data points (K-means, DBSCAN)
    - Dimensionality Reduction: Reduces features (PCA, t-SNE)
    - Anomaly Detection: Finds outliers
    
    3. Reinforcement Learning
    Reinforcement learning trains agents through rewards and penalties.
    Applications include:
    - Game playing (Chess, Go)
    - Robotics
    - Autonomous systems
    
    Key Concepts:
    
    Training Data: The dataset used to train the model
    Features: Input variables that describe the data
    Labels: The target outputs we want to predict
    Overfitting: When a model memorizes noise instead of learning patterns
    Underfitting: When a model is too simple to capture patterns
    Cross-validation: Technique to evaluate model generalization
    Hyperparameters: Settings that control the learning process
    Loss Function: Measures how wrong predictions are
    Optimization: Process of minimizing the loss function
    
    Common ML Workflows:
    
    1. Data Collection: Gather relevant data
    2. Data Preprocessing: Clean and prepare data
    3. Feature Engineering: Create meaningful features
    4. Model Selection: Choose appropriate algorithm
    5. Training: Fit model to training data
    6. Evaluation: Test on validation/test data
    7. Hyperparameter Tuning: Optimize parameters
    8. Deployment: Put model into production
    
    Best Practices:
    
    - Always split data into train, validation, and test sets
    - Normalize/standardize features
    - Handle missing values appropriately
    - Avoid data leakage from test to train sets
    - Monitor model performance in production
    - Retrain models periodically with new data
    
    Popular Python Libraries:
    
    - Scikit-learn: General ML algorithms
    - TensorFlow: Deep learning framework
    - PyTorch: Deep learning with dynamic graphs
    - Pandas: Data manipulation
    - NumPy: Numerical computing
    - Matplotlib: Data visualization
    """
    
    # Initialize the RAG pipeline
    print("\n1️⃣  Initializing RAG System...")
    pipeline = RAGPipeline()
    
    print("2️⃣  Loading document...")
    pipeline.setup(ml_document, source_type="raw")
    
    # Test questions
    test_questions = [
        "What are the main types of machine learning?",
        "Explain the difference between overfitting and underfitting",
        "What is a loss function in machine learning?",
        "Name some popular Python ML libraries"
    ]
    
    print("\n" + "="*70)
    print(" ANSWERING TEST QUESTIONS")
    print("="*70)
    
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📌 Question {i}: {question}")
        print("-" * 70)
        
        # Get answer from RAG system
        result = pipeline.answer_question(question, k=4)
        results.append(result)
        
        # Display answer
        print(f"\n💡 Answer:\n{result['answer']}")
        
        # Show retrieval scores
        print(f"\n📊 Retrieval Confidence Scores:")
        for j, score in enumerate(result['retrieval_scores'], 1):
            confidence = "🟢 High" if score > 0.75 else "🟡 Medium" if score > 0.5 else "🔴 Low"
            print(f"   Chunk {j}: {score:.4f} {confidence}")
    
    # Summary
    print("\n" + "="*70)
    print(" SYSTEM SUMMARY")
    print("="*70)
    
    metrics = pipeline.generate_metrics_report()
    
    print(f"""
    ✅ RAG System Performance:
    
    Questions Answered:        {len(results)}
    Average Retrieval Score:   {sum(sum(r['retrieval_scores']) / len(r['retrieval_scores']) for r in results) / len(results):.4f}
    
    📊 Vector Store Configuration:
    - Model:                   {metrics['embedding_configuration']['model_name']}
    - Embedding Dimension:     {metrics['embedding_configuration']['embedding_dimension']}
    - Total Indexed Documents: {metrics['vector_store_configuration']['indexed_documents']}
    - Retrieval Strategy:      Top-4 Chunks with Similarity Scoring
    
    📄 Chunking Strategy:
    - Chunk Size:              {metrics['chunking_profile']['chunk_size']} characters
    - Chunk Overlap:           {metrics['chunking_profile']['chunk_overlap']} characters
    - Total Chunks Created:    {metrics['chunking_profile']['total_chunks']}
    - Average Chunk Length:    {metrics['chunking_profile']['avg_chunk_size']:.0f} characters
    
    🤖 Language Model:
    - Model:                   {metrics['language_model_setup']['model_name']}
    - Context Window:          {metrics['language_model_setup']['context_window']:,} tokens
    - Max Output:              {metrics['language_model_setup']['max_tokens']} tokens
    """)
    
    # Save results
    print("\n💾 Saving results...")
    output_path = Path.cwd() / "demo_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "questions": test_questions,
            "results": results,
            "metrics": metrics
        }, f, indent=2, default=str)
    
    print(f"✅ Results saved to {output_path}\n")

if __name__ == "__main__":
    main()
