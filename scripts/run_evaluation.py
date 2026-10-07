import json, os, sys, re
from pathlib import Path

from rich import print_json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.metrics import accuracy_score, f1_score
from src.inference.llm_client import run_baseline, run_rag, run_kg_rag, get_client
from src.retrieval.context_builder import ContextBuilder
from src.graph.neo_client import Neo4jClient

# questions_path = "data/raw/LaMP_2/dev_questions.json",
BASE_DIR = Path(__file__).resolve().parent.parent

def clean_tag(tag: str) -> str:
    tag = tag.lower()
    tag = re.sub(r'^(predicted\s+)?tag:\s*', '', tag)
    tag = re.sub(r'[^a-z0-9\s-]', '', tag)
    return tag.strip()

def evaluate(n_samples=20):
    print("Loading development dataset...")
    data_path = BASE_DIR / "data" / "raw" / "LaMP_2" / "dev_questions.json"
    output_path = BASE_DIR / "data" / "raw" / "LaMP_2" / "dev_outputs.json"
    
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        with open(output_path, "r", encoding="utf-8") as f:
            raw_outputs = json.load(f)
            
        golds = raw_outputs.get("golds", raw_outputs)
        output_map = {item["id"]: item["output"] for item in golds}
    except FileNotFoundError:
        print("Error: Could not find dev dataset JSON files in data/raw/LaMP_2/")
        print("Please ensure they are downloaded before running evaluation.")
        return

    db = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")
    user_records = db.run_query("MATCH (u:User) RETURN DISTINCT u.user_id AS uid")
    valid_uids = {str(r["uid"]) for r in user_records} if user_records else set()

    valid_samples = [q for q in questions if str(q.get("user_id", q.get("id"))) in valid_uids]
    
    if not valid_samples:
        print("Warning: No samples found for the known Neo4j user IDs. Using random samples.")
        test_samples = questions[:n_samples]
    else:
        test_samples = valid_samples[:n_samples]

    print(f"Loaded {len(test_samples)} valid samples for evaluation.\n")

    db = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")
    cb = ContextBuilder(db_client=db)
    
    # Pre-initialize LLM client
    llm_client = get_client()

    results = {"Baseline": [], "Text RAG": [], "KG-RAG": []}
    ground_truth = []

    print("-" * 60)
    for i, sample in enumerate(test_samples, 1):
        uid = str(sample.get("user_id", sample.get("id")))
        query = sample["input"]
        gold = output_map.get(sample["id"], "").lower().strip()
        ground_truth.append(gold)
        
        print(f"[{i}/{len(test_samples)}] User {uid} (Gold tag: '{gold}')")
        
        base_pred = run_baseline(uid, query).lower()
        results["Baseline"].append(base_pred)
        
        rag_pred = run_rag(uid, query).lower()
        results["Text RAG"].append(rag_pred)

        kg_ctx = cb.get_context(uid)
        candidate_tags = cb.get_user_candidate_tags_bfs(uid)

        kg_pred = clean_tag(run_kg_rag(uid, query, kg_ctx, candidate_tags=candidate_tags))
        results["KG-RAG"].append(kg_pred)
        
        print(f"  - Baseline Pred: '{base_pred}'")
        print(f"  - Text RAG Pred: '{rag_pred}'")
        print(f"  - KG-RAG Pred:   '{kg_pred}'")
        print(f"    - Candidate Tags Pred: '{candidate_tags}'")
        print("-" * 60)

    db.close()

    print("\n" + "=" * 50)
    print("FINAL EVALUATION RESULTS")
    print("=" * 50)
    print(f"{'System':<15} | {'Accuracy':>10} | {'Macro-F1':>10}")
    print("-" * 43)
    
    for system_name, preds in results.items():
        clean_preds = [p.replace("tag: ", "").strip() for p in preds]
        acc = accuracy_score(ground_truth, clean_preds)
        f1 = f1_score(ground_truth, clean_preds, average="macro", zero_division=0)
        print(f"{system_name:<15} | {acc:>10.3f} | {f1:>10.3f}")
    
    print("=" * 50)

if __name__ == "__main__":
    evaluate(n_samples=50)
