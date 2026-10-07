import re
from sklearn.metrics import accuracy_score, f1_score
from src.data_loader.dataset_parser import DataParser
from src.inference.llm_client import run_baseline, run_rag, run_kg_rag
from src.graph.neo_client import Neo4jClient
from src.retrieval.context_builder import ContextBuilder

def print_results_table(results: dict):
    print("\n" + "=" * 50)
    print(f"{'System':<15} | {'Accuracy':<12} | {'Macro F1':<12}")
    print("-" * 50)
    for system, metrics in results.items():
        print(f"{system:<15} | {metrics['accuracy']:<12.4f} | {metrics['macro_f1']:<12.4f}")
    print("=" * 50 + "\n")

def clean_tag(tag: str) -> str:
    tag = str(tag).lower().strip()
    tag = re.sub(r'[^a-z0-9\s-]', '', tag) # Remove quotes, periods, etc.
    return tag


def evaluate_all():
    parser = DataParser(
        questions_path="data/raw/LaMP_2/dev_questions.json",
        outputs_path="data/raw/LaMP_2/dev_outputs.json",
    )
    questions, output_map = parser.load()

    # 2. Иницијализација на ContextBuilder
    db_client = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="password123")
    context_builder = ContextBuilder(db_client)

    # 3. Филтрирај само за корисниците што ти се изградени во Neo4j (пр. првите неколку)
    processed_users = {"110", "111", "112", "113", "114", "115", "116", "117"}
    test_questions = [q for q in questions if q.get("user_id", q["id"]) in processed_users]

    systems = ["baseline", "rag", "kg_rag"]
    results = {}

    for system_name in systems:
        predictions = []
        ground_truth = []

        print(f"Running evaluation for [{system_name}]...")

        for sample in test_questions:
            sample_id = sample["id"]
            user_id = sample.get("user_id", sample_id)
            query = sample["input"]
            expected = output_map[sample_id]

            # 4. Повикување на функциите со правилни аргументи
            if system_name == "baseline":
                pred = run_baseline(user_id, query)
            elif system_name == "rag":
                pred = run_rag(user_id, query)
            elif system_name == "kg_rag":
                # Влечење на контекст од графот
                kg_context = context_builder.get_context(user_id)
                # Праќање на контекстот кон LLM клиентот
                pred = run_kg_rag(user_id, query, kg_context)

            pred_clean = clean_tag(pred)
            expected_clean = clean_tag(expected)

            predictions.append(pred_clean)
            ground_truth.append(expected_clean)

        results[system_name] = {
            "accuracy": accuracy_score(ground_truth, predictions),
            "macro_f1": f1_score(ground_truth, predictions, average="macro", zero_division=0),
        }

    print_results_table(results)
    db_client.close()

if __name__ == "__main__":
    evaluate_all()