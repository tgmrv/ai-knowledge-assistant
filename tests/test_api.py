def test_ask_returns_answer(api_client, rag_mock):
    question = "Как создать заказ?"
    answer = "Заказ создаётся через POST /orders."
    rag_mock.answer.return_value = answer

    response = api_client.post("/ask", json={"question": f"  {question}  "})

    assert response.status_code == 200
    assert response.json() == {"answer": answer}
    rag_mock.answer.assert_awaited_once_with(question)


def test_ask_requires_question(api_client, rag_mock):
    response = api_client.post("/ask", json={})

    assert response.status_code == 422
    rag_mock.answer.assert_not_called()
