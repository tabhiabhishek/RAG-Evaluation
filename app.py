import streamlit as st
import yaml
import pandas as pd
from evaluator import run_evaluation, load_prompt

st.set_page_config(page_title="RAG Evaluator", page_icon="📊", layout="wide")

st.title("📊 RAG/LLM Evaluation & Prompt Versioning")
st.markdown("Compare different prompt versions using a **Custom LLM-as-a-Judge** (Faithfulness, Answer Relevance, Context Precision).")

# Load available prompt versions
with open("prompts.yaml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Select Prompt Version to Evaluate")
    version = st.selectbox("Prompt Version", list(prompts.keys()), format_func=lambda x: prompts[x]["name"])
    st.info(f"**Description:** {prompts[version]['description']}\n\n**Template:**\n`	ext\n{load_prompt(version)}\n`")

with col2:
    st.subheader("Action")
    if st.button("🚀 Run Custom LLM Evaluation", type="primary"):
        with st.spinner("Running local LLM-as-a-Judge evaluation (this may take 30-60 seconds)..."):
            try:
                df = run_evaluation(version)
                st.success("Evaluation Complete!")
                
                # Display Average Scores
                st.write("### 📈 Average Scores")
                avg_faith = df["Faithfulness"].mean()
                avg_rel = df["Relevance"].mean()
                avg_prec = df["Context Precision"].mean()
                
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Avg Faithfulness", f"{avg_faith:.2f} / 5.0", help="5.0 = No hallucinations")
                col_b.metric("Avg Relevance", f"{avg_rel:.2f} / 5.0", help="5.0 = Directly answers the question")
                col_c.metric("Avg Context Precision", f"{avg_prec:.2f} / 5.0", help="5.0 = Retrieved chunks are highly relevant")
                
                # Display Detailed Breakdown
                st.write("### 🔍 Detailed Breakdown")
                st.dataframe(df, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"Error during evaluation: {str(e)}")
                st.warning("Make sure Ollama is running and you have pulled 'qwen2.5' (ollama pull qwen2.5)")
