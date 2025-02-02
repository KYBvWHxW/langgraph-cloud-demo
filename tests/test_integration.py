from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_assistants():
    response = client.get("/v1/assistants")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["id"] == "asst_default"

def test_get_assistant():
    response = client.get("/v1/assistants/asst_default")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "asst_default"
    assert data["name"] == "Simple Chat Assistant"

def test_create_thread():
    response = client.post("/v1/threads", json={
        "assistant_id": "asst_default",
        "metadata": {"test": True}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_id"] == "asst_default"
    assert "id" in data
    assert data["id"].startswith("thread_")

def test_chat_flow():
    # Create thread
    thread_response = client.post("/v1/threads", json={
        "assistant_id": "asst_default"
    })
    thread_id = thread_response.json()["id"]
    
    # Create message
    message_response = client.post(f"/v1/threads/{thread_id}/messages", json={
        "role": "user",
        "content": "What is LangChain?"
    })
    assert message_response.status_code == 200
    
    # Create run
    run_response = client.post(f"/v1/threads/{thread_id}/runs")
    assert run_response.status_code == 200
    run_id = run_response.json()["id"]
    
    # Get run
    get_run_response = client.get(f"/v1/threads/{thread_id}/runs/{run_id}")
    assert get_run_response.status_code == 200
    assert get_run_response.json()["status"] == "completed"

def test_rate_limiter():
    # Test rate limiting by making multiple requests
    for _ in range(61):  # One over the limit
        response = client.get("/v1/health")
    assert response.status_code == 429
    assert response.text == "Rate limit exceeded"

def test_redis_caching():
    # First request should cache the response
    response1 = client.get("/v1/assistants/asst_default")
    assert response1.status_code == 200
    
    # Second request should use cached response
    response2 = client.get("/v1/assistants/asst_default")
    assert response2.status_code == 200
    assert response2.json() == response1.json()
