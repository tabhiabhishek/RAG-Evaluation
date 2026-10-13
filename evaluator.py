import yaml
import pandas as pd
import json
import requests

def load_prompt(version: str) -> str:
    with open("prompts.yaml", "r", encoding="utf-8") as f:
        prompts = yaml.safe_load(f)
    return prompts[version]["template"]

def get_llm_judge_score(question: str, context: str, answer: str) -> dict:
    """
    Custom LLM-as-a-Judge using Ollama's native JSON formatting.
    Zero external evaluation library dependencies!
    """
    judge_prompt = f"""You are an expert evaluator of RAG systems. Evaluate the following based on a scale of 1 to 5.
Question: {question}
Context: {context}
Answer: {answer}

Provide your evaluation in strictly valid JSON format with the following keys:
- "faithfulness": (1-5) Does the answer rely ONLY on the provided context? (5 = completely faithful, 1 = hallucinated)
- "relevance": (1-5) Does the answer directly address the question? (5 = highly relevant, 1 = irrelevant)
- "context_precision": (1-5) Is the provided context actually useful for answering the question? (5 = highly useful, 1 = useless)

JSON Output:"""

    payload = {
        "model": "qwen2.5",
        "prompt": judge_prompt,
        "stream": False,
        "format": "json"
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        # Parse the JSON response from the model
        return json.loads(result["response"])
    except Exception as e:
        return {"faithfulness": 0, "relevance": 0, "context_precision": 0, "error": str(e)}

# Dummy Dataset for Evaluation
dummy_data = [
    {
        "question": "What is the capital of France?",
        "ground_truth": "Paris",
        "context": "Paris is the capital and most populous city of France.",
        "answer": "The capital of France is Paris."
    },
    {
        "question": "Who invented the telephone?",
        "ground_truth": "Alexander Graham Bell",
        "context": "The telephone was invented by Alexander Graham Bell in 1876.",
        "answer": "Alexander Graham Bell invented the telephone."
    },
    {
        "question": "What is the speed of light?",
        "ground_truth": "I don't know based on the provided context.",
        "context": "The Earth revolves around the sun.",
        "answer": "I don't know based on the provided context."
    }
]

def run_evaluation(prompt_version: str):
    prompt_template = load_prompt(prompt_version)
    
    results_data = []
    
    for item in dummy_data:
        # Simulate answer generation based on prompt version
        if prompt_version == "v2_strict" and "speed of light" in item["question"].lower():
            answer = "I don't know based on the provided context."
        else:
            answer = item["ground_truth"]
            
        # Get scores from our custom LLM Judge
        scores = get_llm_judge_score(item["question"], item["context"], answer)
        
        results_data.append({
            "Question": item["question"],
            "Context": item["context"],
            "Answer": answer,
            "Faithfulness": scores.get("faithfulness", 0),
            "Relevance": scores.get("relevance", 0),
            "Context Precision": scores.get("context_precision", 0)
        })
    
    df = pd.DataFrame(results_data)
    return df
