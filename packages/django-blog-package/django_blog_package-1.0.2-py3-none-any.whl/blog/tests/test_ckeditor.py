"""
Tests for CKEditor integration in the blog package.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from blog.models import Post, Category
from ckeditor.fields import RichTextField


class CKEditorIntegrationTest(TestCase):
    """Test CKEditor integration with the blog package."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Technology", slug="technology", description="Technology related posts"
        )

    def test_post_content_field_is_richtextfield(self):
        """Test that Post.content field is RichTextField."""
        field = Post._meta.get_field("content")
        self.assertIsInstance(field, RichTextField)

    def test_ckeditor_content_saves_and_retrieves_html(self):
        """Test that CKEditor content with HTML saves and retrieves correctly."""
        html_content = """
        <h2>This is a heading</h2>
        <p>This is a paragraph with <strong>bold text</strong> and <em>italic text</em>.</p>
        <ul>
            <li>List item 1</li>
            <li>List item 2</li>
        </ul>
        <blockquote>This is a blockquote</blockquote>
        """

        post = Post.objects.create(
            title="Test Post with HTML",
            slug="test-post-with-html",
            content=html_content,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        # Retrieve the post and check content
        retrieved_post = Post.objects.get(pk=post.pk)
        self.assertEqual(retrieved_post.content, html_content)
        self.assertIn("<h2>This is a heading</h2>", retrieved_post.content)
        self.assertIn("<strong>bold text</strong>", retrieved_post.content)

    def test_ckeditor_content_with_images(self):
        """Test that CKEditor content with image references works."""
        html_with_image = """
        <p>This is a post with an image:</p>
        <img src="/media/blog/images/test.jpg" alt="Test Image">
        <p>Some text after the image.</p>
        """

        post = Post.objects.create(
            title="Test Post with Image",
            slug="test-post-with-image",
            content=html_with_image,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        retrieved_post = Post.objects.get(pk=post.pk)
        self.assertIn('<img src="/media/blog/images/test.jpg"', retrieved_post.content)
        self.assertIn('alt="Test Image"', retrieved_post.content)

    def test_ckeditor_content_with_links(self):
        """Test that CKEditor content with links works."""
        html_with_links = """
        <p>Check out these links:</p>
        <ul>
            <li><a href="https://example.com">Example Website</a></li>
            <li><a href="https://django-project.com" target="_blank">Django Project</a></li>
        </ul>
        """

        post = Post.objects.create(
            title="Test Post with Links",
            slug="test-post-with-links",
            content=html_with_links,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        retrieved_post = Post.objects.get(pk=post.pk)
        self.assertIn('href="https://example.com"', retrieved_post.content)
        self.assertIn('target="_blank"', retrieved_post.content)

    def test_ckeditor_content_preserves_formatting(self):
        """Test that CKEditor preserves formatting like line breaks and spacing."""
        formatted_content = """
        <p>First paragraph.</p>
        <p>Second paragraph with<br>line break.</p>
        <pre><code>def hello_world():
    print("Hello, World!")</code></pre>
        """

        post = Post.objects.create(
            title="Test Formatted Post",
            slug="test-formatted-post",
            content=formatted_content,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        retrieved_post = Post.objects.get(pk=post.pk)
        self.assertIn("<br>", retrieved_post.content)
        self.assertIn("<pre><code>", retrieved_post.content)

    def test_ckeditor_admin_configuration(self):
        """Test that CKEditor is properly configured in admin."""
        from blog.admin import PostAdminForm

        form = PostAdminForm()
        widget = form.fields["content"].widget

        # Check that CKEditor widget is used
        from ckeditor.widgets import CKEditorWidget

        self.assertIsInstance(widget, CKEditorWidget)

        # Check that custom configuration is used
        self.assertEqual(widget.config_name, "blog_editor")

    def test_ckeditor_content_in_excerpt_generation(self):
        """Test that excerpt generation works with CKEditor HTML content."""
        html_content = """
        <h2>Introduction</h2>
        <p>This is the first paragraph of the blog post content that should be used to generate an excerpt when no explicit excerpt is provided.</p>
        <p>This second paragraph should not be included in the auto-generated excerpt.</p>
        """

        post = Post.objects.create(
            title="Test Excerpt Generation",
            slug="test-excerpt-generation",
            content=html_content,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        # Check that excerpt was auto-generated from HTML content
        self.assertIsNotNone(post.excerpt)
        self.assertIn("This is the first paragraph", post.excerpt)
        # Should not include HTML tags in excerpt
        self.assertNotIn("<p>", post.excerpt)
        self.assertNotIn("</p>", post.excerpt)

    def test_ckeditor_content_with_special_characters(self):
        """Test that CKEditor handles special characters correctly."""
        content_with_specials = """
        <p>Special characters: &amp; &lt; &gt; &quot; &apos;</p>
        <p>Math symbols: π ≈ 3.14, ∑(x²) = 100</p>
        <p>Emojis: 😀 🚀 📚</p>
        """

        post = Post.objects.create(
            title="Test Special Characters",
            slug="test-special-characters",
            content=content_with_specials,
            author=self.user,
            category=self.category,
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(timezone.datetime(2024, 1, 15, 12, 0, 0)),
        )

        retrieved_post = Post.objects.get(pk=post.pk)
        self.assertIn("&amp;", retrieved_post.content)
        self.assertIn("π ≈ 3.14", retrieved_post.content)
