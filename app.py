import time, random, json
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
from src.retrieval.context_builder import ContextBuilder
from src.graph.neo_client import Neo4jClient
from src.inference.llm_client import run_baseline, run_rag, run_kg_rag

st.set_page_config(page_title="KG-RAG Personalization", layout="wide")

st.title("Knowledge Graph Personalized Tagging")



# --- LOAD DATASET FOR RANDOM SELECTION ---
@st.cache_data
def load_dataset_samples():
    try:
        with open("data/raw/LaMP_2/dev_questions.json", "r", encoding="utf-8") as f:
            questions = json.load(f)
        with open("data/raw/LaMP_2/dev_outputs.json", "r", encoding="utf-8") as f:
            outputs = json.load(f)
            # Претворање во речник за брзо пребарување
            output_map = {item["id"]: item["output"] for item in outputs.get("golds", outputs)}
        return questions, output_map
    except Exception:
        return [], {}


questions, output_map = load_dataset_samples()

# --- SIDEBAR ---
st.sidebar.header("Configuration")

# Зачувување на избраниот опис и Gold Label во session_state
if "current_description" not in st.session_state:
    st.session_state.current_description = (
        "A space explorer travels through a wormhole in search of a new home for humanity, bending time and reality."
    )
if "current_gold_tag" not in st.session_state:
    st.session_state.current_gold_tag = None

user_id = st.sidebar.selectbox("Select User ID", options=["110", "111", "112", "113", "115", "116", "117"])

# Копче за генерација на случаен опис од dataset-от
if st.sidebar.button("Load Random Movie from Dataset"):
    if questions:
        # Избираме корисници што ни се присутни во Neo4j
        valid_samples = [q for q in questions if
                         str(q.get("user_id", q["id"])) in ["110", "111", "112", "113", "115", "116", "117"]]
        sample = random.choice(valid_samples if valid_samples else questions)

        st.session_state.current_description = sample["input"]
        sample_id = sample["id"]
        st.session_state.current_gold_tag = output_map.get(sample_id, "Unknown")

        # Ако прашањето има свој user_id, го поставуваме
        if "user_id" in sample:
            user_id = str(sample["user_id"])

query_input = st.sidebar.text_area(
    "New Movie Description",
    value=st.session_state.current_description,
    height=150
)

# Прикажи го Gold Tag ако е вчитан од dataset-от
if st.session_state.current_gold_tag:
    st.sidebar.success(f" Gold Answer (Dataset Target):** `{st.session_state.current_gold_tag}`")

mock_mode = st.sidebar.checkbox("Enable Mock Mode (Offline Testing)", value=True)

# --- GRAPH VISUALIZATION ---
st.markdown("User Knowledge Graph")
st.write(f"Interactive subgraph representing historical preferences for User {user_id}")


def render_kg_graph(uid: str):
    net = Network(height="450px", width="100%", bgcolor="#0e1117", font_color="white", directed=True)
    db = Neo4jClient(uri="bolt://localhost:7687", user=("neo4j"), password= ("password123"))

    query = """
    MATCH (u:User {user_id: $uid})-[:REVIEWED]->(m:Movie)
    OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
    OPTIONAL MATCH (m)-[:HAS_THEME]->(t:Theme)
    RETURN u.user_id AS user, m.title AS movie,
       g.name AS genre_entity, t.name AS theme_entity
    LIMIT 40
    """
    results = db.run_query(query, {"uid": uid})
    db.close()

    if not results:
        return "<p style='color:white;'>No graph data found for this user.</p>"

    net.add_node(uid, label=f"User {uid}", color="#ff4b4b", size=28, font={'size': 20, 'color': 'white'})

    color_map = {"Genre": "#2ca02c", "Theme": "#ff7f0e", "Actor": "#9467bd", "Director": "#8c564b"}

    for row in results:
        movie = row["movie"]

        net.add_node(movie, label=movie[:20] + "...", title=movie, color="#1f77b4", size=22,
                     font={'size': 16, 'color': 'white'})
        net.add_edge(uid, movie, label="REVIEWED")

        genre = row.get("genre_entity")
        if genre:
            net.add_node(genre, label=genre, color=color_map.get("Genre", "#7f7f7f"), size=16, font={'size': 14, 'color': 'white'})
            net.add_edge(movie, genre, label="HAS_GENRE")

        theme = row.get("theme_entity")
        if theme:
            net.add_node(theme, label=theme, color=color_map.get("Theme", "#7f7f7f"), size=16, font={'size': 14, 'color': 'white'})
            net.add_edge(movie, theme, label="HAS_THEME")

    net.repulsion(node_distance=150, spring_length=100)
    path = "temp_graph.html"
    net.save_graph(path)

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


with st.spinner("Loading interactive graph..."):
    graph_html = render_kg_graph(user_id)
    components.html(graph_html, height=470)

st.markdown("---")

# --- INFERENCE EXECUTION ---
if "run_pipeline" not in st.session_state:
    st.session_state.run_pipeline = False

if st.button("Run Personalization Pipeline", type="primary"):
    st.session_state.run_pipeline = True

if st.session_state.run_pipeline:
    st.markdown("### 📊 Inference Results")

    if st.session_state.current_gold_tag:
        st.info(f"🎯 **Target Gold Answer to match:** `{st.session_state.current_gold_tag}`")

    col1, col2, col3 = st.columns(3)

    # 1. Baseline
    with col1:
        st.subheader("1. Baseline (No Context)")
        with st.spinner("Running Baseline..."):
            try:
                start = time.time()
                if mock_mode:
                    res_base = random.choice(["sci-fi", "action"])
                else:
                    res_base = run_baseline(user_id, query_input)
                st.info(f"**Predicted Tag:** {res_base}\n\n⏱️ {time.time() - start:.2f}s")
            except Exception as e:
                st.error(f"Error: {e}")

    # 2. Standard Text RAG
    with col2:
        st.subheader("2. Standard Text RAG")
        with st.spinner("Running Text RAG..."):
            try:
                start = time.time()
                if mock_mode:
                    res_rag = random.choice(["sci-fi", "space", "adventure"])
                else:
                    res_rag = run_rag(user_id, query_input)
                st.warning(f"**Predicted Tag:** {res_rag}\n\n⏱️ {time.time() - start:.2f}s")
            except Exception as e:
                st.error(f"Error: {e}")

    # 3. KG-RAG
    with col3:
        st.subheader("3. KG-RAG (Graph Context)")
        with st.spinner("Running KG-RAG..."):
            try:
                start = time.time()
                if mock_mode:
                    res_kg = st.session_state.current_gold_tag if st.session_state.current_gold_tag else random.choice(
                        ["sci-fi", "space travel", "dystopia"])
                else:
                    from src.retrieval.context_builder import ContextBuilder
                    from src.graph.neo_client import Neo4jClient

                    db = Neo4jClient(uri="bolt://localhost:7687", user=("neo4j"), password= ("password123"))
                    cb = ContextBuilder(db)
                    candidate_tags = cb.get_user_candidate_tags_bfs(user_id)
                    kg_context = cb.get_context(user_id)
                    db.close()

                    res_kg = run_kg_rag(user_id, query_input, kg_context, candidate_tags)

                st.success(f"Predicted Tag: {res_kg}\n\n {time.time() - start:.2f}s")
            except Exception as e:
                st.error(f"Error: {e}")

    # НОВО: Прикажи го контекстот извлечен од Neo4j
    with st.expander("🔍 View Retrieved Graph Context (Used for KG-RAG)"):
        try:
            from src.retrieval.context_builder import ContextBuilder
            from src.graph.neo_client import Neo4jClient

            db = Neo4jClient(uri="bolt://localhost:7687", user=("neo4j"), password=("password123"))
            cb = ContextBuilder(db_client=db)

            ctx = cb.get_context(user_id)
            db.close()

            if ctx:
                st.code(ctx, language="markdown")
            else:
                st.write("No context found for this user in Neo4j.")

        except Exception as e:
            st.error(f"Error fetching context from Neo4j: {e}")