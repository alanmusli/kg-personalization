# Knowledge Graph Augmented Retrieval (GraphRAG) for LLM Personalization

This project implements a personalized movie tagging and categorization system evaluated on the **LaMP-2 benchmark** (Language Model Personalization). It combines a **Neo4j Knowledge Graph** with a local Large Language Model (**Qwen 2.5 7B** via Ollama) to deliver structured, noise-free personal context for accurate personalized predictions.

---

## Prerequisites

Make sure you have the following installed on your machine:
1. **Python 3.11+**
2. **Docker Desktop** (for running the Neo4j graph database)
3. **Ollama** (for local LLM inference)

---

## 🛠️ Installation & Setup Guide

### 1. Clone the Repository & Setup Environment
```bash
git clone https://github.com/alanmusli/kg-personalization.git
cd kg-personalization

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt


#Run the Ollama
ollama run qwen2.5:7b

#Run the container
docker run -d \
  --name neo4j-lamp \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest

#Initialize Database Schema & Build Knowledge Graph

#Create Constraints and Indexes in Neo4j:
python scripts/neo4j_start.py

#Extract Entities & Populate the Graph:
python scripts/start.py


#Running the application

#Option 1:
streamlit run app.py

#Option 2:
python scripts/run_evaluation.py
