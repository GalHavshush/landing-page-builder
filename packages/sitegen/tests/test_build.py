import io
import re
import zipfile

from sitegen import SiteDocument, build
from sitegen.cli import main
from sitegen.export import make_zip
from sitegen.starters import list_starters, load_starter


def starter_with_base_url(**site) -> SiteDocument:
    doc = load_starter("clean")
    data = doc.model_dump(mode="json")
    data["site"].update(base_url="https://example.com", **site)
    return SiteDocument.model_validate(data)


def test_all_starters_build_without_issues():
    for name in list_starters():
        doc = load_starter(name)
        issues = [
            i for i in build(doc).issues if i.level == "warning" and "base_url" not in i.message
        ]
        assert not issues, (name, issues)


def test_output_files_and_layout():
    files = build(starter_with_base_url()).files
    assert {"index.html", "services/index.html", "about/index.html", "404.html"} <= set(files)
    assert {"css/site.css", "js/site.js", "robots.txt", "sitemap.xml"} <= set(files)


def test_pages_use_only_relative_urls_but_404_is_root_relative():
    files = build(starter_with_base_url()).files
    for path, data in files.items():
        if not path.endswith(".html") or path == "404.html":
            continue
        html = data.decode()
        assert not re.search(r'(?:href|src)="/', html), path
    assert 'href="../css/site.css"' in files["about/index.html"].decode()
    assert 'href="/css/site.css"' in files["404.html"].decode()


def test_seo_head_sitemap_robots():
    files = build(starter_with_base_url()).files
    about = files["about/index.html"].decode()
    assert "<title>About | Northside Studio</title>" in about
    assert 'rel="canonical" href="https://example.com/about/"' in about
    assert 'content="Learn more about our story."' in about
    home = files["index.html"].decode()
    assert "<title>Northside Studio – Thoughtful design" in home
    assert "<loc>https://example.com/about/</loc>" in files["sitemap.xml"].decode()
    assert "Sitemap: https://example.com/sitemap.xml" in files["robots.txt"].decode()
    assert 'name="robots" content="noindex"' in files["404.html"].decode()


def test_noindex_pages_are_left_out_of_sitemap():
    doc = starter_with_base_url()
    doc.pages[2].seo.noindex = True
    sitemap = build(doc).files["sitemap.xml"].decode()
    assert "/about/" not in sitemap


def test_missing_base_url_warns_and_skips_sitemap():
    result = build(load_starter("clean"))
    assert "sitemap.xml" not in result.files
    assert any("base_url" in i.message for i in result.issues)


def test_zip_contains_site_readme_and_source():
    doc = starter_with_base_url()
    zf = zipfile.ZipFile(io.BytesIO(make_zip(build(doc).files, doc)))
    names = set(zf.namelist())
    assert {"index.html", "README.txt", "export.json", "css/site.css"} <= names
    assert SiteDocument.model_validate_json(zf.read("export.json")) == doc


def test_zip_is_deterministic():
    doc = starter_with_base_url()
    files = build(doc).files
    assert make_zip(files, doc) == make_zip(files, doc)


def test_cli_init_build_zip(tmp_path):
    doc_path, out = tmp_path / "site.json", tmp_path / "out"
    assert main(["init", "clean", str(doc_path), "--name", "Acme"]) == 0
    assert main(["build", str(doc_path), str(out), "--zip", str(tmp_path / "s.zip")]) == 0
    assert "Acme" in (out / "index.html").read_text()
    assert (tmp_path / "s.zip").exists()
