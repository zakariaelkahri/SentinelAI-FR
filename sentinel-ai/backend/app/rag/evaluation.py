

# import json
# import logging
# from app.rag.retriever import get_retriever
# from app.rag.llm import local_model
# from app.rag.prompt import structured_prompt_template

# logger = logging.getLogger(__name__)

# MLFLOW_URI = "http://mlflow:5000"


# TEST_CASES = [
#     {
#         "query_id": "q1",
#         "query": "Quels sont les traitements recommandés pour le prurit en médecine adulte ?",
#         "relevant_docs": [
#             "prurit traitement gale",
#             "prurit antimycosique",
#             "prurit antihistaminique",
#             "prurit dermocorticoides"
#         ]
#     },
#     {
#         "query_id": "q2",
#         "query": "Que faut-il faire en cas de suspicion d'infection dans un contexte de prurit ?",
#         "relevant_docs": [
#             "Si suspicion d'infection, se référer au chapitre Infection cutanée."
#         ]
#     },
#     {
#         "query_id": "q3",
#         "query": "Que faire en cas de traumatisme en dent de lait avec dent expulsée ?",
#         "relevant_docs": [
#             "Si Dent expulsée : =>NE PAS REMETTRE",
#             "On ne veut pas léser le gemme de la dent définitive qui est dessous.",
#             "Rechercher la dent pour vérifier qu'il s'agit bien d'une expulsion (et non d'une impaction, ou encore d'une inhalation/ ingestion).",
#             "Contrôle de la plaie gingivale (désinfection avec compresse chlorhexidine si possible, morsure dans une compresse si ça saigne).",
#             "On ne fait rien quand c'est une dent de lait, la petite souris passera en avance."
#         ]
#     },
#     {
#         "query_id": "q4",
#         "query": "Quels sont les signes cliniques d'un abcès ou d'une cellulite dentaire chez l'enfant ?",
#         "relevant_docs": [
#             "ABCES (boule de pus) / CELLULITE (inflammation et gonflement +++)",
#             "A Les signes cliniques : - Empâtement autour de la dent et dans le vestibule - Souvent petite boule de pus sur le coté de la gencive - Souvent légère mobilité de la dent sans choc préalable - ADP (Adénopathie = ganglions) périphérique en relation - Début de tuméfaction externe ou Cellulite dans les cas plus avancés",
#             "B Les signes à vérifier si cellulite (gonflement++ de la joue) : Cellulite en bas : Vérifier que le plancher (sous la langue) est souple Cellulite en haut : Vérifier que l'arrière de la gorge et le palais mou ne sont pas gonflés"
#         ]
#     },
#     {
#         "query_id": "q5",
#         "query": "Que faut-il faire en cas de brûlure de méduse en médecine adulte ?",
#         "relevant_docs": [
#             "Retirer les filaments visibles avec une pince ou à la main doublement gantée, puis appliquer de la mousse à raser. Racler délicatement la mousse contenant les nématocystes ainsi piégés à l'aide d'une abaisse langue.",
#             "Rincer abondamment la piqûre à l'eau de mer ou au sérum physiologique. La toxine étant thermolabile, l'eau peut être chaude sans brûler. Le rinçage dure jusqu'à disparition des symptômes (environ 30 minutes).",
#             "Après décontamination, la plaie sera séchée puis enduite d'anesthésiques locaux ou de corticoïdes de classe moyenne ou faible (Locapred) dont les effets bénéfiques ont été démontrés principalement devant la persistance des lésions après 24 heures.",
#             "Vérifier et éventuellement remettre à jour la vaccination antitétanique (c.f. Protocole).",
#             "Les lésions ulcérées seront nettoyées quotidiennement et recouvertes d'une fine couche de lotion antiseptique non allergisante (chlorhexidine aqueuse 0.2%).",
#             "Les traitements antalgiques de palier I à II, rarement III sont indiqués (échelle thérapeutique de la douleur selon l'OMS).",
#             "Toujours anticiper une réaction anaphylactique et donc être préparé à y répondre par les antihistaminiques et les corticoïdes par voie veineuse."
#         ]
#     }
# ]


# def precision_at_k(retrieved_docs: list, relevant_snippets: list[str], k: int) -> float:
#     """Precision@k = (relevant docs in top-k) / k"""
#     top_k = retrieved_docs[:k]
#     if not top_k:
#         return 0.0
#     relevant_count = sum(
#         1 for doc in top_k
#         if any(s.lower() in doc.page_content.lower() for s in relevant_snippets)
#     )
#     return relevant_count / k


# def recall_at_k(retrieved_docs: list, relevant_snippets: list[str], k: int) -> float:
#     """Recall@k = (relevant snippets found in top-k) / (total relevant snippets)"""
#     if not relevant_snippets:
#         return 0.0
#     top_k = retrieved_docs[:k]
#     found = sum(
#         1 for snippet in relevant_snippets
#         if any(snippet.lower() in doc.page_content.lower() for doc in top_k)
#     )
#     return found / len(relevant_snippets)


# def answer_relevance(question: str, answer: str, llm) -> float:
#     """Use LLM to judge answer relevance to the question. Returns 0.0-1.0."""
#     prompt = (
#         "You are an evaluation judge. Rate the RELEVANCE of the answer to the question.\n\n"
#         f"Question: {question}\nAnswer: {answer}\n\n"
#         "Rate from 0.0 to 1.0 (0.0=irrelevant, 0.5=partial, 1.0=fully relevant).\n"
#         "Respond with ONLY a float number, nothing else."
#     )
#     response = llm.invoke(prompt)
#     return _parse_score(response.content)


# def faithfulness(context: str, answer: str, llm) -> float:
#     """Use LLM to judge if the answer is faithful to the context. Returns 0.0-1.0."""
#     prompt = (
#         "You are an evaluation judge. Rate the FAITHFULNESS of the answer with respect to the context.\n\n"
#         f"Context: {context}\nAnswer: {answer}\n\n"
#         "Rate from 0.0 to 1.0 (0.0=hallucinated, 0.5=partial, 1.0=fully faithful).\n"
#         "Respond with ONLY a float number, nothing else."
#     )
#     response = llm.invoke(prompt)
#     return _parse_score(response.content)


# def _parse_score(text: str) -> float:
#     for token in text.strip().split():
#         try:
#             score = float(token)
#             if 0.0 <= score <= 1.0:
#                 return score
#         except ValueError:
#             continue
#     return 0.0


# def run_evaluation(k: int = 5) -> dict:
#     llm = local_model()
#     results = []

#     for tc in TEST_CASES:
#         qid, query, relevant = tc["query_id"], tc["query"], tc["relevant_docs"]
#         logger.info(f"Evaluating {qid}: {query[:60]}...")

#         docs = get_retriever().invoke(query)
#         context = "\n\n".join([d.page_content for d in docs])
#         answer = llm.invoke(structured_prompt_template.format(context=context, question=query)).content

#         result = {
#             "query_id": qid,
#             "query": query,
#             "precision_at_k": precision_at_k(docs, relevant, k),
#             "recall_at_k": recall_at_k(docs, relevant, k),
#             "answer_relevance": answer_relevance(query, answer, llm),
#             "faithfulness": faithfulness(context, answer, llm),
#         }
#         results.append(result)
#         logger.info(
#             f"  P@{k}={result['precision_at_k']:.2f}  R@{k}={result['recall_at_k']:.2f}  "
#             f"Relevance={result['answer_relevance']:.2f}  Faithfulness={result['faithfulness']:.2f}"
#         )

#     n = len(results)
#     evaluation = {
#         "k": k,
#         "num_test_cases": n,
#         "per_query_results": results,
#         "avg_precision_at_k": sum(r["precision_at_k"] for r in results) / n,
#         "avg_recall_at_k": sum(r["recall_at_k"] for r in results) / n,
#         "avg_answer_relevance": sum(r["answer_relevance"] for r in results) / n,
#         "avg_faithfulness": sum(r["faithfulness"] for r in results) / n,
#     }

#     try:
#         import mlflow
#         mlflow.set_tracking_uri(MLFLOW_URI)
#         mlflow.set_experiment("RAG_Evaluation")
#         with mlflow.start_run(run_name=f"RAG_Eval_k{k}"):
#             mlflow.log_param("k", k)
#             mlflow.log_metric("avg_precision_at_k", evaluation["avg_precision_at_k"])
#             mlflow.log_metric("avg_recall_at_k", evaluation["avg_recall_at_k"])
#             mlflow.log_metric("avg_answer_relevance", evaluation["avg_answer_relevance"])
#             mlflow.log_metric("avg_faithfulness", evaluation["avg_faithfulness"])
#             for r in results:
#                 mlflow.log_metric(f"precision_at_k_{r['query_id']}", r["precision_at_k"])
#                 mlflow.log_metric(f"recall_at_k_{r['query_id']}", r["recall_at_k"])
#                 mlflow.log_metric(f"answer_relevance_{r['query_id']}", r["answer_relevance"])
#                 mlflow.log_metric(f"faithfulness_{r['query_id']}", r["faithfulness"])
#             mlflow.log_text(json.dumps(evaluation, indent=2, ensure_ascii=False), "evaluation_results.json")
#         logger.info("Evaluation metrics logged to MLflow.")
#     except Exception as e:
#         logger.warning(f"MLflow logging failed: {e}")

#     return evaluation


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     r = run_evaluation(k=5)
#     print(f"\nAvg P@k={r['avg_precision_at_k']:.4f}  R@k={r['avg_recall_at_k']:.4f}  "
#           f"Relevance={r['avg_answer_relevance']:.4f}  Faithfulness={r['avg_faithfulness']:.4f}")
