def test_health(client):
    """Test that health check returns properly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
