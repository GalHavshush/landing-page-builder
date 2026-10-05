def signup(client, email="rosa@example.com", password="correct horse", name="Rosa"):
    r = client.post("/auth/register", json={"email": email, "password": password, "name": name})
    assert r.status_code == 201, r.text
    return r.json()


def make_project(client, name="Rosa Bakery", template="clean"):
    r = client.post("/projects", json={"name": name, "template": template})
    assert r.status_code == 201, r.text
    return r.json()


def image_bytes(
    fmt="PNG", size=(40, 30), color=(200, 40, 40, 255), mode="RGBA", exif_orientation=None
):
    import io

    from PIL import Image

    img = Image.new(mode, size, color if mode == "RGBA" else color[:3])
    out = io.BytesIO()
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        exif[0x010F] = "SecretCameraMaker"  # metadata that must not survive
        kwargs["exif"] = exif
    img.save(out, fmt, **kwargs)
    return out.getvalue()


def upload(client, project_id, data, name="photo.png", content_type="image/png"):
    return client.post(f"/projects/{project_id}/assets", files={"file": (name, data, content_type)})


def export_zip(client, project_id):
    """Create an export and download it: returns (export json, zipfile.ZipFile)."""
    import io
    import zipfile

    made = client.post(f"/projects/{project_id}/exports")
    assert made.status_code == 201, made.text
    export = made.json()
    dl = client.get(f"/projects/{project_id}/exports/{export['id']}/download")
    assert dl.status_code == 200
    return export, zipfile.ZipFile(io.BytesIO(dl.content))
