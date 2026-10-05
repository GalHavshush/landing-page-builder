from datetime import datetime

from sitegen import AssetFile, SiteDocument, build
from sitegen.posts import Post, format_date
from sitegen.preview import render_post_preview
from sitegen.sections import create_section


def post(i: int, lang="en", group=None, **kw) -> Post:
    return Post(
        id=f"post_{i}",
        lang=lang,
        translation_group=group or f"grp_{i}",
        slug=kw.pop("slug", f"post-{i}"),
        title=kw.pop("title", f"Post number {i}"),
        excerpt=kw.pop("excerpt", f"Excerpt {i}"),
        body_md=kw.pop("body_md", f"Body of **post {i}**"),
        published_at=kw.pop("published_at", datetime(2026, 1, i)),
        **kw,
    )


def blog_doc(languages=("en",), base_url="https://example.com") -> SiteDocument:
    blog = create_section("blog_list").model_dump(mode="json")
    return SiteDocument.model_validate(
        {
            "site": {
                "name": "Rosa",
                "base_url": base_url,
                "languages": list(languages),
                "nav": [{"label": "Blog", "page": "pg_blog"}],
            },
            "pages": [
                {"id": "pg_home", "slug": "", "title": "Home", "sections": []},
                {"id": "pg_blog", "slug": "blog-index", "title": "Blog", "sections": [blog]},
            ],
        }
    )


def test_post_pages_and_blog_list_are_generated():
    files = build(blog_doc(), posts=[post(1), post(2)]).files
    assert {"blog/post-1/index.html", "blog/post-2/index.html"} <= set(files)
    index = files["blog-index/index.html"].decode()
    assert index.index("Post number 2") < index.index("Post number 1")  # newest first
    assert 'href="../blog/post-2/index.html"' in index


def test_post_page_content_seo_and_back_link():
    html = build(blog_doc(), posts=[post(3)]).files["blog/post-3/index.html"].decode()
    assert "<h1>Post number 3</h1>" in html
    assert "<strong>post 3</strong>" in html  # markdown rendered
    assert 'rel="canonical" href="https://example.com/blog/post-3/"' in html
    assert 'property="og:type" content="article"' in html
    assert 'content="Excerpt 3"' in html
    assert "3 January 2026" in html
    assert 'href="../../blog-index/index.html"' in html  # back to the page that lists posts


def test_raw_html_and_scripts_in_posts_are_neutralised():
    evil = "<script>alert(1)</script>\n\n[x](javascript:alert(2))\n\n<img src=x onerror=alert(3)>"
    html = build(blog_doc(), posts=[post(1, body_md=evil)]).files["blog/post-1/index.html"].decode()
    assert "<script>alert" not in html
    assert 'href="javascript:' not in html
    assert "<img src=x" not in html


def test_assets_referenced_from_markdown_resolve_to_files():
    p = post(1, body_md="![A loaf](asset:asset_abc123def456)", cover="asset_abc123def456")
    files = build(
        blog_doc(), {"asset_abc123def456": AssetFile("loaf.webp", b"img", width=4, height=3)}, [p]
    ).files
    page = files["blog/post-1/index.html"].decode()
    path = next(n for n in files if n.startswith("assets/"))
    assert f'src="../../{path}"' in page
    assert f'content="https://example.com/{path}"' in page  # cover as social image


def test_sitemap_rss_and_translations():
    doc = blog_doc(("en", "he"))
    posts = [post(1, "en", "g1"), post(2, "he", "g1", slug="poast-1", title="פוסט")]
    files = build(doc, posts=posts).files
    sitemap = files["sitemap.xml"].decode()
    assert (
        "https://example.com/blog/post-1/" in sitemap
        and "https://example.com/he/blog/poast-1/" in sitemap
    )
    assert 'hreflang="he" href="https://example.com/he/blog/poast-1/"' in sitemap
    rss = files["blog/feed.xml"].decode()
    assert "<title>Post number 1</title>" in rss and "פוסט" not in rss
    assert "<title>פוסט</title>" in files["he/blog/feed.xml"].decode()
    he = files["he/blog/poast-1/index.html"].decode()
    assert 'dir="rtl"' in he and 'hreflang="en"' in he  # language switcher links to the translation


def test_blog_list_only_shows_posts_of_the_current_language():
    doc = blog_doc(("en", "he"))
    files = build(doc, posts=[post(1, "en", "g1"), post(2, "he", "g2", title="רק בעברית")]).files
    assert "רק בעברית" not in files["blog-index/index.html"].decode()
    assert "רק בעברית" in files["he/blog-index/index.html"].decode()


def test_empty_blog_list_shows_message():
    html = build(blog_doc()).files["blog-index/index.html"].decode()
    assert "No posts yet" in html


def test_no_feed_without_base_url():
    files = build(blog_doc(base_url=""), posts=[post(1)]).files
    assert "blog/feed.xml" not in files


def test_post_preview_renders_unsaved_drafts():
    html = render_post_preview(blog_doc(), post(1, title="Draft title")).html
    assert "Draft title" in html and 'data-section-type=' not in html and "<style>" in html


def test_dates_are_localised():
    assert format_date(datetime(2026, 3, 5), "en") == "5 March 2026"
    assert format_date(datetime(2026, 3, 5), "he") == "5 מרץ 2026"
    assert format_date(datetime(2026, 3, 5), "xx") == "5 March 2026"
