def test_register_existing_user(client):
    # Crear usuario
    client.post("/auth/register", json={
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "pass123"
    })

    # Intentar registrar mismo username
    response = client.post("/auth/register", json={
        "username": "duplicate",
        "email": "another@example.com",
        "password": "newpass"
    })
    assert response.status_code == 400
    assert b"usuario ya existe" in response.data

    # Intentar registrar mismo email
    response = client.post("/auth/register", json={
        "username": "anotheruser",
        "email": "duplicate@example.com",
        "password": "newpass"
    })
    assert response.status_code == 400
    assert b"email ya existe" in response.data


def test_login_invalid_credentials(client):
    # Intentar login sin usuario registrado
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "1234"
    })
    assert response.status_code == 401
    assert b"Credenciales incorrectas" in response.data


def test_get_profile_requires_auth(client):
    response = client.get("/auth/profile")
    assert response.status_code == 401  # Requiere JWT


def test_get_profile_success(client):
    # Registro y login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "123456"
    })

    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "123456"
    })
    token = login_response.json["token"]

    # Obtener perfil con token
    headers = {"Authorization": f"Bearer {token}"}
    profile_response = client.get("/auth/profile", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json["username"] == "testuser"
    assert profile_response.json["email"] == "testuser@example.com"
