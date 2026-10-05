def signup(client, email="rosa@example.com", password="correct horse", name="Rosa"):
    r = client.post("/auth/register", json={"email": email, "password": password, "name": name})
    assert r.status_code == 201, r.text
    return r.json()


def make_project(client, name="Rosa Bakery", template="clean"):
    r = client.post("/projects", json={"name": name, "template": template})
    assert r.status_code == 201, r.text
    return r.json()
