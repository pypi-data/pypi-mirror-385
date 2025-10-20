"""
Example demonstrating basic usage of air-socials library.

This example shows how to:
1. Build individual SEO, Open Graph, and Twitter Card tags
2. Use the convenience function to build a complete head tag
3. Render HTML pages with proper social metadata
"""

import json

from air import Body, Div, H1, Html, P

from air_socials import (
    build_favicon_links,
    build_json_ld,
    build_open_graph,
    build_seo_meta,
    build_social_head,
    build_twitter_card,
)


def example_individual_tags():
    """Example: Build individual tag groups."""
    print("=" * 60)
    print("EXAMPLE 1: Building Individual Tag Groups")
    print("=" * 60)

    # Build SEO meta tags
    seo_tags = build_seo_meta(
        title="My Awesome Article",
        description="This is a comprehensive guide to building awesome websites",
        keywords=["python", "web development", "air framework"],
        canonical_url="https://example.com/articles/awesome-guide",
        author="Jane Developer",
    )

    # Build Open Graph tags
    og_tags = build_open_graph(
        title="My Awesome Article",
        description="This is a comprehensive guide to building awesome websites",
        url="https://example.com/articles/awesome-guide",
        image="https://example.com/images/og-image.jpg",
        image_alt="Article cover image showing web development concepts",
        image_width=1200,
        image_height=630,
        type="article",
        site_name="Example Blog",
        article_author="Jane Developer",
        article_published_time="2025-01-15T10:00:00Z",
        article_section="Web Development",
        article_tags=["python", "tutorial", "beginner-friendly"],
    )

    # Build Twitter Card tags
    twitter_tags = build_twitter_card(
        card_type="summary_large_image",
        site="@exampleblog",
        creator="@janedev",
    )

    # Build favicon links
    favicon_tags = build_favicon_links(
        favicon_ico="/static/favicon.ico",
        favicon_svg="/static/favicon.svg",
        apple_touch_icon="/static/apple-touch-icon.png",
    )

    print("\nSEO Meta Tags:")
    for tag in seo_tags:
        print(f"  {tag.render()}")

    print("\nOpen Graph Tags:")
    for tag in og_tags:
        print(f"  {tag.render()}")

    print("\nTwitter Card Tags:")
    for tag in twitter_tags:
        print(f"  {tag.render()}")

    print("\nFavicon Links:")
    for tag in favicon_tags:
        print(f"  {tag.render()}")


def example_complete_head():
    """Example: Build a complete head tag with all social elements."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Building Complete Head Tag")
    print("=" * 60)

    # Build a complete head tag with all social and SEO elements
    head = build_social_head(
        title="Air Framework - Build Beautiful Web Apps",
        description="A modern Python framework for building web applications with ease",
        url="https://air-framework.dev",
        image="https://air-framework.dev/images/social-card.jpg",
        image_alt="Air Framework logo and tagline",
        keywords=["python", "web framework", "html", "components"],
        site_name="Air Framework",
        twitter_site="@airframework",
        author="Air Team",
        theme_color="#007bff",
    )

    print("\nComplete Head Tag:")
    print(head.pretty_render())


def example_with_json_ld():
    """Example: Build head with JSON-LD structured data."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Including JSON-LD Structured Data")
    print("=" * 60)

    # Create JSON-LD structured data
    article_data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "Getting Started with Air Framework",
        "author": {
            "@type": "Person",
            "name": "Jane Developer",
            "url": "https://example.com/authors/jane",
        },
        "datePublished": "2025-01-15T10:00:00Z",
        "dateModified": "2025-01-15T14:30:00Z",
        "image": "https://example.com/images/article-cover.jpg",
        "publisher": {
            "@type": "Organization",
            "name": "Example Blog",
            "logo": {
                "@type": "ImageObject",
                "url": "https://example.com/logo.png",
            },
        },
    }

    # Build JSON-LD script tag
    json_ld_tag = build_json_ld(json.dumps(article_data, indent=2))

    # Build complete head with JSON-LD
    # Note: Extra children must be passed as positional args before keyword args
    head = build_social_head(
        json_ld_tag,  # Extra children come first
        title="Getting Started with Air Framework",
        description="Learn how to build your first web app with Air",
        url="https://example.com/articles/getting-started",
        image="https://example.com/images/article-cover.jpg",
        site_name="Example Blog",
        twitter_site="@exampleblog",
        twitter_creator="@janedev",
        og_type="article",
    )

    print("\nHead with JSON-LD:")
    print(head.pretty_render())


def example_full_page():
    """Example: Build a complete HTML page with social metadata."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Complete HTML Page")
    print("=" * 60)

    # Build complete HTML page
    page = Html(
        build_social_head(
            title="Welcome to Air Socials",
            description="Helper library for building social media cards and SEO tags with Air",
            url="https://github.com/kentro-tech/air-socials",
            image="https://github.com/kentro-tech/air-socials/raw/main/social-card.jpg",
            keywords=["python", "air", "seo", "social media", "open graph"],
            site_name="Air Socials",
            twitter_site="@kentrotech",
            author="Kentro Tech",
            theme_color="#2563eb",
        ),
        Body(
            Div(
                H1("Welcome to Air Socials"),
                P(
                    "This is a helper library for building social media cards, "
                    "SEO tags, and head elements with the Air framework."
                ),
                P(
                    "Your page now has perfect Open Graph tags, Twitter Cards, "
                    "and SEO metadata!"
                ),
                class_="container",
            ),
        ),
    )

    print("\nComplete HTML Page:")
    print(page.pretty_render())


if __name__ == "__main__":
    example_individual_tags()
    example_complete_head()
    example_with_json_ld()
    example_full_page()
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
