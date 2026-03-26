import logging

from app.rag.llm import local_model
from app.rag.prompt import structured_prompt_template
from app.rag.retriever import get_retriever

logger = logging.getLogger(__name__)


TEST_CASES = [
    {
        "query_id": "q1",
        "query": "What should happen when a complaint is made against a security officer?",
        "relevant_docs": [
            "the complaint must be recorded and investigated",
            "The Company will appoint an investigator",
            "A full investigation will be carried out",
            "Security Officer's notebook will normally have a complete entry",
        ],
    },
    {
        "query_id": "q2",
        "query": "What is expected from a security officer before commencing duty?",
        "relevant_docs": [
            "A Security Officer is expected to have a full and complete knowledge of the duties, procedures, instructions and specifics of your location before commencing duty",
            "lacking in knowledge of any aspect of these instructions",
        ],
    },
    {
        "query_id": "q3",
        "query": "What actions should officers take during patrol when they notice suspicious packages or hazards?",
        "relevant_docs": [
            "keep a lookout for and take appropriate action regarding suspicious packages",
            "fire hazards, water leaks, gas leaks",
            "use your pocket book",
        ],
    },
    {
        "query_id": "q4",
        "query": "What reporting records are required after an incident on site?",
        "relevant_docs": [
            "Anything that happens on site that is outside of the standard operations will require an incident report",
            "use your notes from your pocket book to compile your report",
            "Daily Occurrence Book",
        ],
    },
    {
        "query_id": "q5",
        "query": "What should a security officer do when discovering a fire?",
        "relevant_docs": [
            "ACTIONS ON DISCOVERY OF A FIRE",
            "Inform",
            "Restrict",
            "Extinguish OR Evacuate",
        ],
    },
]


def precision_at_k(retrieved_docs: list, relevant_snippets: list[str], k: int) -> float:
    """Precision@k = (relevant docs in top-k) / k."""
    top_k = retrieved_docs[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(
        1
        for doc in top_k
        if any(s.lower() in doc.page_content.lower() for s in relevant_snippets)
    )
    return relevant_count / k


def recall_at_k(retrieved_docs: list, relevant_snippets: list[str], k: int) -> float:
    """Recall@k = (relevant snippets found in top-k) / total relevant snippets."""
    if not relevant_snippets:
        return 0.0
    top_k = retrieved_docs[:k]
    found = sum(
        1
        for snippet in relevant_snippets
        if any(snippet.lower() in doc.page_content.lower() for doc in top_k)
    )
    return found / len(relevant_snippets)


def answer_relevance(question: str, answer: str, llm) -> float:
    """Use LLM to judge answer relevance to the question. Returns 0.0-1.0."""
    prompt = (
        "You are an evaluation judge. Rate the RELEVANCE of the answer to the question.\n\n"
        f"Question: {question}\nAnswer: {answer}\n\n"
        "Rate from 0.0 to 1.0 (0.0=irrelevant, 0.5=partial, 1.0=fully relevant).\n"
        "Respond with ONLY a float number, nothing else."
    )
    response = llm.invoke(prompt)
    return _parse_score(response.content)


def faithfulness(context: str, answer: str, llm) -> float:
    """Use LLM to judge if the answer is faithful to the context. Returns 0.0-1.0."""
    prompt = (
        "You are an evaluation judge. Rate the FAITHFULNESS of the answer with respect to the context.\n\n"
        f"Context: {context}\nAnswer: {answer}\n\n"
        "Rate from 0.0 to 1.0 (0.0=hallucinated, 0.5=partial, 1.0=fully faithful).\n"
        "Respond with ONLY a float number, nothing else."
    )
    response = llm.invoke(prompt)
    return _parse_score(response.content)


def _parse_score(text: str) -> float:
    for token in text.strip().split():
        try:
            score = float(token)
            if 0.0 <= score <= 1.0:
                return score
        except ValueError:
            continue
    return 0.0


def run_evaluation(k: int = 5) -> dict:
    llm = local_model()
    results = []
    retriever = get_retriever()

    for tc in TEST_CASES:
        qid, query, relevant = tc["query_id"], tc["query"], tc["relevant_docs"]
        logger.info("Evaluating %s: %s...", qid, query[:60])

        docs = retriever.invoke(query)
        context = "\n\n".join([d.page_content for d in docs])
        prompt = structured_prompt_template.format(
            context=context,
            question=query,
            response_language="English",
        )
        answer = llm.invoke(prompt).content

        result = {
            "query_id": qid,
            "query": query,
            "precision_at_k": precision_at_k(docs, relevant, k),
            "recall_at_k": recall_at_k(docs, relevant, k),
            "answer_relevance": answer_relevance(query, answer, llm),
            "faithfulness": faithfulness(context, answer, llm),
        }
        results.append(result)
        logger.info(
            "  P@%s=%.2f  R@%s=%.2f  Relevance=%.2f  Faithfulness=%.2f",
            k,
            result["precision_at_k"],
            k,
            result["recall_at_k"],
            result["answer_relevance"],
            result["faithfulness"],
        )

    n = len(results)
    evaluation = {
        "k": k,
        "num_test_cases": n,
        "per_query_results": results,
        "avg_precision_at_k": sum(r["precision_at_k"] for r in results) / n,
        "avg_recall_at_k": sum(r["recall_at_k"] for r in results) / n,
        "avg_answer_relevance": sum(r["answer_relevance"] for r in results) / n,
        "avg_faithfulness": sum(r["faithfulness"] for r in results) / n,
    }

    return evaluation


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = run_evaluation(k=5)
    print(
        f"\nAvg P@k={r['avg_precision_at_k']:.4f}  R@k={r['avg_recall_at_k']:.4f}  "
        f"Relevance={r['avg_answer_relevance']:.4f}  Faithfulness={r['avg_faithfulness']:.4f}"
    )
