import io

def test_upload_video_requires_auth(client):
    response = client.post("/video/upload", data={})
    assert response.status_code == 401  # JWT requerido

def test_status_returns_404_for_unknown_video(client):
    response = client.get("/video/status/fakevideoid")
    assert response.status_code == 404
