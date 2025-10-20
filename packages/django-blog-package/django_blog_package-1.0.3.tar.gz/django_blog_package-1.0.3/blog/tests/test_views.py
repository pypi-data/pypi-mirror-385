from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
from blog.models import Post, Category, Tag, Comment
from blog.forms import CommentForm


class PostListViewTest(TestCase):
    """Test cases for PostListView"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )

        # Create published posts
        for i in range(15):
            Post.objects.create(
                title=f"Test Post {i}",
                slug=f"test-post-{i}",
                author=self.user,
                category=self.category,
                content=f"Content for post {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.now() - timedelta(days=i),
            )

    def test_post_list_view_status_code(self):
        """Test that post list view returns 200 status code"""
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)

    def test_post_list_view_template_used(self):
        """Test that correct template is used"""
        response = self.client.get(reverse("blog:post_list"))
        self.assertTemplateUsed(response, "blog/post_list.html")

    def test_post_list_view_context(self):
        """Test that context contains expected data"""
        response = self.client.get(reverse("blog:post_list"))
        self.assertIn("posts", response.context)
        self.assertIn("page_title", response.context)
        self.assertEqual(response.context["page_title"], "Latest Posts")

    def test_post_list_pagination(self):
        """Test that pagination works correctly"""
        response = self.client.get(reverse("blog:post_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["posts"]), 10)  # Default pagination

    def test_post_list_only_published_posts(self):
        """Test that only published posts are shown"""
        # Create a draft post
        Post.objects.create(
            title="Draft Post",
            author=self.user,
            category=self.category,
            content="Draft content",
            status=Post.DRAFT,
            publish_date=timezone.now(),
        )

        response = self.client.get(reverse("blog:post_list"))
        posts = response.context["posts"]

        # Should only show published posts
        self.assertEqual(posts.count(), 10)  # First page of published posts
        draft_posts = [post for post in posts if post.status == Post.DRAFT]
        self.assertEqual(len(draft_posts), 0)


class PostDetailViewTest(TestCase):
    """Test cases for PostDetailView"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            category=self.category,
            content="This is a test post content.",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

    def test_post_detail_view_status_code(self):
        """Test that post detail view returns 200 status code"""
        url = self.post.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_detail_view_template_used(self):
        """Test that correct template is used"""
        url = self.post.get_absolute_url()
        response = self.client.get(url)
        self.assertTemplateUsed(response, "blog/post_detail.html")

    def test_post_detail_view_context(self):
        """Test that context contains expected data"""
        url = self.post.get_absolute_url()
        response = self.client.get(url)

        self.assertIn("post", response.context)
        self.assertIn("comment_form", response.context)
        self.assertIn("comments", response.context)
        self.assertIn("related_posts", response.context)
        self.assertIn("view_count", response.context)

        self.assertEqual(response.context["post"], self.post)
        self.assertIsInstance(response.context["comment_form"], CommentForm)

    def test_post_detail_view_only_published_posts(self):
        """Test that draft posts return 404"""
        draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            category=self.category,
            content="Draft content",
            status=Post.DRAFT,
            publish_date=timezone.now(),
        )

        url = draft_post.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_related_posts(self):
        """Test that related posts are shown"""
        # Create related posts in same category
        for i in range(3):
            Post.objects.create(
                title=f"Related Post {i}",
                author=self.user,
                category=self.category,
                content=f"Related content {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.now(),
            )

        url = self.post.get_absolute_url()
        response = self.client.get(url)
        related_posts = response.context["related_posts"]

        self.assertEqual(len(related_posts), 3)


class CategoryPostListViewTest(TestCase):
    """Test cases for CategoryPostListView"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.another_category = Category.objects.create(
            name="Another Category", slug="another-category"
        )

        # Create posts in test category
        for i in range(5):
            Post.objects.create(
                title=f"Test Post {i}",
                author=self.user,
                category=self.category,
                content=f"Content {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.now(),
            )

        # Create posts in another category
        Post.objects.create(
            title="Another Category Post",
            author=self.user,
            category=self.another_category,
            content="Another content",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

    def test_category_post_list_view_status_code(self):
        """Test that category post list view returns 200 status code"""
        response = self.client.get(
            reverse("blog:category_posts", kwargs={"slug": "test-category"})
        )
        self.assertEqual(response.status_code, 200)

    def test_category_post_list_view_context(self):
        """Test that context contains category and filtered posts"""
        response = self.client.get(
            reverse("blog:category_posts", kwargs={"slug": "test-category"})
        )

        self.assertIn("category", response.context)
        self.assertIn("posts", response.context)
        self.assertIn("page_title", response.context)

        self.assertEqual(response.context["category"], self.category)
        self.assertEqual(
            response.context["page_title"], f"Posts in {self.category.name}"
        )

        # Should only show posts from this category
        posts = response.context["posts"]
        for post in posts:
            self.assertEqual(post.category, self.category)

    def test_category_post_list_view_invalid_category(self):
        """Test that invalid category returns 404"""
        response = self.client.get(
            reverse("blog:category_posts", kwargs={"slug": "non-existent-category"})
        )
        self.assertEqual(response.status_code, 404)


class TagPostListViewTest(TestCase):
    """Test cases for TagPostListView"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.tag = Tag.objects.create(name="Test Tag", slug="test-tag")
        self.another_tag = Tag.objects.create(name="Another Tag", slug="another-tag")

        # Create posts with test tag
        for i in range(3):
            post = Post.objects.create(
                title=f"Test Post {i}",
                author=self.user,
                category=self.category,
                content=f"Content {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.now(),
            )
            post.tags.add(self.tag)

        # Create post with another tag
        another_post = Post.objects.create(
            title="Another Tag Post",
            author=self.user,
            category=self.category,
            content="Another content",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )
        another_post.tags.add(self.another_tag)

    def test_tag_post_list_view_status_code(self):
        """Test that tag post list view returns 200 status code"""
        response = self.client.get(
            reverse("blog:tag_posts", kwargs={"slug": "test-tag"})
        )
        self.assertEqual(response.status_code, 200)

    def test_tag_post_list_view_context(self):
        """Test that context contains tag and filtered posts"""
        response = self.client.get(
            reverse("blog:tag_posts", kwargs={"slug": "test-tag"})
        )

        self.assertIn("tag", response.context)
        self.assertIn("posts", response.context)
        self.assertIn("page_title", response.context)

        self.assertEqual(response.context["tag"], self.tag)
        self.assertEqual(
            response.context["page_title"], f"Posts tagged with {self.tag.name}"
        )

        # Should only show posts with this tag
        posts = response.context["posts"]
        for post in posts:
            self.assertIn(self.tag, post.tags.all())

    def test_tag_post_list_view_invalid_tag(self):
        """Test that invalid tag returns 404"""
        response = self.client.get(
            reverse("blog:tag_posts", kwargs={"slug": "non-existent-tag"})
        )
        self.assertEqual(response.status_code, 404)


class PostSearchViewTest(TestCase):
    """Test cases for PostSearchView"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")

        # Create posts with different content
        Post.objects.create(
            title="Python Tutorial",
            author=self.user,
            category=self.category,
            content="Learn Python programming language",
            excerpt="Python programming guide",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

        Post.objects.create(
            title="Django Framework",
            author=self.user,
            category=self.category,
            content="Building web applications with Django",
            excerpt="Django web framework tutorial",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

        Post.objects.create(
            title="JavaScript Basics",
            author=self.user,
            category=self.category,
            content="Introduction to JavaScript",
            excerpt="JavaScript programming",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

    def test_post_search_view_status_code(self):
        """Test that search view returns 200 status code"""
        response = self.client.get(reverse("blog:post_search"), {"q": "python"})
        self.assertEqual(response.status_code, 200)

    def test_post_search_view_empty_query(self):
        """Test search with empty query"""
        response = self.client.get(reverse("blog:post_search"), {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts"]), 0)

    def test_post_search_view_context(self):
        """Test that context contains search results and query"""
        response = self.client.get(reverse("blog:post_search"), {"q": "python"})

        self.assertIn("posts", response.context)
        self.assertIn("search_query", response.context)
        self.assertIn("page_title", response.context)

        self.assertEqual(response.context["search_query"], "python")
        self.assertEqual(response.context["page_title"], 'Search Results for "python"')

    def test_post_search_view_results(self):
        """Test that search returns correct results"""
        # Search for "python"
        response = self.client.get(reverse("blog:post_search"), {"q": "python"})
        posts = response.context["posts"]
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts[0].title, "Python Tutorial")

        # Search for "django"
        response = self.client.get(reverse("blog:post_search"), {"q": "django"})
        posts = response.context["posts"]
        self.assertEqual(posts.count(), 1)
        self.assertEqual(posts[0].title, "Django Framework")

        # Search for "programming" (should match multiple posts)
        response = self.client.get(reverse("blog:post_search"), {"q": "programming"})
        posts = response.context["posts"]
        self.assertEqual(posts.count(), 2)

    def test_post_search_view_no_results(self):
        """Test search with no matching results"""
        response = self.client.get(reverse("blog:post_search"), {"q": "nonexistent"})
        posts = response.context["posts"]
        self.assertEqual(posts.count(), 0)


class ArchiveViewsTest(TestCase):
    """Test cases for archive views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")

        # Create posts with different dates
        self.post1 = Post.objects.create(
            title="Post 1",
            author=self.user,
            category=self.category,
            content="Content 1",
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(datetime(2024, 1, 15)),
        )

        self.post2 = Post.objects.create(
            title="Post 2",
            author=self.user,
            category=self.category,
            content="Content 2",
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(datetime(2024, 2, 20)),
        )

        self.post3 = Post.objects.create(
            title="Post 3",
            author=self.user,
            category=self.category,
            content="Content 3",
            status=Post.PUBLISHED,
            publish_date=timezone.make_aware(datetime(2024, 2, 25)),
        )

    def test_post_archive_view_status_code(self):
        """Test that post archive view returns 200 status code"""
        response = self.client.get(reverse("blog:post_archive"))
        self.assertEqual(response.status_code, 200)

    def test_year_archive_view_status_code(self):
        """Test that year archive view returns 200 status code"""
        response = self.client.get(reverse("blog:year_archive", kwargs={"year": 2024}))
        self.assertEqual(response.status_code, 200)

    def test_month_archive_view_status_code(self):
        """Test that month archive view returns 200 status code"""
        response = self.client.get(
            reverse("blog:month_archive", kwargs={"year": 2024, "month": 2})
        )
        self.assertEqual(response.status_code, 200)

    def test_year_archive_view_context(self):
        """Test that year archive view has correct context"""
        response = self.client.get(reverse("blog:year_archive", kwargs={"year": 2024}))

        self.assertIn("year", response.context)
        self.assertIn("posts", response.context)
        self.assertEqual(response.context["year"].year, 2024)

        # Should show all posts from 2024
        posts = response.context["posts"]
        self.assertEqual(len(posts), 3)

    def test_month_archive_view_context(self):
        """Test that month archive view has correct context"""
        response = self.client.get(
            reverse("blog:month_archive", kwargs={"year": 2024, "month": 2})
        )

        self.assertIn("month", response.context)
        self.assertIn("posts", response.context)

        # Should show only posts from February 2024
        posts = response.context["posts"]
        self.assertEqual(len(posts), 2)
        for post in posts:
            self.assertEqual(post.publish_date.month, 2)
            self.assertEqual(post.publish_date.year, 2024)

    def test_archive_views_empty_years(self):
        """Test archive views for years with no posts"""
        response = self.client.get(reverse("blog:year_archive", kwargs={"year": 2023}))
        self.assertEqual(response.status_code, 404)


class CommentViewTest(TestCase):
    """Test cases for add_comment view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user,
            category=self.category,
            content="Test content",
            status=Post.PUBLISHED,
            publish_date=timezone.now(),
        )

    def test_add_comment_authenticated_user(self):
        """Test adding comment as authenticated user"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("blog:add_comment", kwargs={"post_id": self.post.id}),
            {
                "author_name": "Test User",
                "author_email": "test@example.com",
                "content": "This is a test comment.",
            },
        )

        # Should redirect to post detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.post.get_absolute_url() + "#comments")

        # Comment should be created and auto-approved
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.content, "This is a test comment.")
        self.assertTrue(comment.is_approved)

    def test_add_comment_unauthenticated_user(self):
        """Test adding comment as unauthenticated user"""
        response = self.client.post(
            reverse("blog:add_comment", kwargs={"post_id": self.post.id}),
            {
                "author_name": "Anonymous User",
                "author_email": "anonymous@example.com",
                "content": "This is an anonymous comment.",
            },
        )

        # Should redirect to post detail page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.post.get_absolute_url() + "#comments")

        # Comment should be created but not auto-approved
        comment = Comment.objects.get(post=self.post)
        self.assertEqual(comment.content, "This is an anonymous comment.")
        self.assertFalse(comment.is_approved)

    def test_add_comment_invalid_post(self):
        """Test adding comment to non-existent post"""
        response = self.client.post(
            reverse("blog:add_comment", kwargs={"post_id": 999}),
            {
                "author_name": "Test User",
                "author_email": "test@example.com",
                "content": "This comment should fail.",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_add_comment_invalid_form(self):
        """Test adding comment with invalid form data"""
        response = self.client.post(
            reverse("blog:add_comment", kwargs={"post_id": self.post.id}),
            {
                "author_name": "",  # Required field
                "author_email": "invalid-email",  # Invalid email
                "content": "",  # Required field
            },
        )

        # Should redirect back to post (form errors handled by redirect)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.post.get_absolute_url())

        # No comment should be created
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)
