import sys
import types


def test_assistant_ask_success(
    client_factory,
    monkeypatch,
    fake_async_session_cls,
    build_test_user_fn,
):
    operator_user = build_test_user_fn("operator1", "operator")
    fake_db = fake_async_session_cls()

    fake_pipeline = types.ModuleType("app.rag.pipeline")
    fake_pipeline.answer_question = lambda question: f"mocked answer: {question}"
    monkeypatch.setitem(sys.modules, "app.rag.pipeline", fake_pipeline)

    client = client_factory(fake_db, operator_user)
    response = client.post(
        "/api/v1/assistant/security/ask",
        json={"question": "What should I do in case of fire?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "What should I do in case of fire?"
    assert body["answer"].startswith("mocked answer:")


def test_assistant_ask_runtime_error_maps_to_503(
    client_factory,
    monkeypatch,
    fake_async_session_cls,
    build_test_user_fn,
):
    operator_user = build_test_user_fn("operator1", "operator")
    fake_db = fake_async_session_cls()

    fake_pipeline = types.ModuleType("app.rag.pipeline")

    def _raise_runtime_error(_question):
        raise RuntimeError("RAG unavailable")

    fake_pipeline.answer_question = _raise_runtime_error
    monkeypatch.setitem(sys.modules, "app.rag.pipeline", fake_pipeline)

    client = client_factory(fake_db, operator_user)
    response = client.post(
        "/api/v1/assistant/security/ask",
        json={"question": "Hello"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "RAG unavailable"





