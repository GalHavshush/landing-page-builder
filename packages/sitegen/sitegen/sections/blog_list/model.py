from typing import Literal

from pydantic import Field
from sitegen.models import BaseSection, Strict, content, design
from sitegen.sections.base import SectionDef


class BlogListProps(Strict):
    heading: str = content("text", "")
    subheading: str = content("textarea", "")
    limit: Literal[0, 3, 6, 9, 12] = design("select", 0, hint="0 shows every post")
    show_excerpt: bool = design("toggle", True)
    show_cover: bool = design("toggle", True)


class BlogListSection(BaseSection):
    type: Literal["blog_list"] = "blog_list"
    variant: Literal["cards", "list"] = "cards"
    props: BlogListProps = Field(default_factory=BlogListProps)


DEF = SectionDef(
    "blog_list",
    "Blog posts",
    BlogListSection,
    BlogListProps,
    defaults={"heading": "From the blog"},
    description="Your latest blog posts. Manage the posts in the Blog tab.",
)
