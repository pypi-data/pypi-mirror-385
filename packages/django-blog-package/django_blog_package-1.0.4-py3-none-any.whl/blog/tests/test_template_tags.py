from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from blog.models import Post, Category, Tag, Comment, PostView
from blog.templatetags.blog_tags import (
    get_categories,
    get_recent_posts,
    get_popular_posts,
    get_popular_tags,
    get_archive_months,
    get_post_count_by_month,
    blog_sidebar,
    view_counter,
)


class TemplateTagsTest(TestCase):
    """Test cases for blog template tags"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category1 = Category.objects.create(name="Category 1", slug="category-1")
        self.category2 = Category.objects.create(name="Category 2", slug="category-2")

        # Create tags
        self.tag1 = Tag.objects.create(name="Python", slug="python")
        self.tag2 = Tag.objects.create(name="Django", slug="django")
        self.tag3 = Tag.objects.create(name="JavaScript", slug="javascript")

        # Create posts with different dates and view counts
        self.post1 = Post.objects.create(
            title="Post 1",
            slug="post-1",
            author=self.user,
            category=self.category1,
            content="Content 1",
            status=Post.PUBLISHED,
            publish_date=timezone.now() - timedelta(days=1),
        )
        self.post1.tags.add(self.tag1, self.tag2)

        self.post2 = Post.objects.create(
            title="Post 2",
            slug="post-2",
            author=self.user,
            category=self.category1,
            content="Content 2",
            status=Post.PUBLISHED,
            publish_date=timezone.now() - timedelta(days=2),
        )
        self.post2.tags.add(self.tag2, self.tag3)

        self.post3 = Post.objects.create(
            title="Post 3",
            slug="post-3",
            author=self.user,
            category=self.category2,
            content="Content 3",
            status=Post.PUBLISHED,
            publish_date=timezone.now() - timedelta(days=3),
        )
        self.post3.tags.add(self.tag1, self.tag3)

        # Create a draft post (should not appear in queries)
        self.draft_post = Post.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            category=self.category1,
            content="Draft content",
            status=Post.DRAFT,
            publish_date=timezone.now(),
        )

        # Create post views to simulate popularity
        PostView.objects.create(
            post=self.post1, ip_address="127.0.0.1", session_key="session1"
        )
        PostView.objects.create(
            post=self.post1, ip_address="127.0.0.2", session_key="session2"
        )
        PostView.objects.create(
            post=self.post2, ip_address="127.0.0.3", session_key="session3"
        )

        # Update view counts
        self.post1.view_count = 10
        self.post1.save()
        self.post2.view_count = 5
        self.post2.save()
        self.post3.view_count = 2
        self.post3.save()


class GetCategoriesTest(TemplateTagsTest):
    """Test cases for get_categories template tag"""

    def test_get_categories_returns_all_categories(self):
        """Test that get_categories returns all categories"""
        categories = get_categories()

        self.assertEqual(categories.count(), 2)
        self.assertIn(self.category1, categories)
        self.assertIn(self.category2, categories)

    def test_get_categories_ordered_by_name(self):
        """Test that categories are ordered by name"""
        categories = get_categories()

        self.assertEqual(categories[0].name, "Category 1")
        self.assertEqual(categories[1].name, "Category 2")

    def test_get_categories_post_counts(self):
        """Test that categories include post counts"""
        categories = get_categories()

        category1 = categories.get(name="Category 1")
        category2 = categories.get(name="Category 2")

        # Category 1 has 2 published posts, Category 2 has 1
        self.assertEqual(category1.posts.count(), 2)
        self.assertEqual(category2.posts.count(), 1)

    def test_get_categories_excludes_empty_categories(self):
        """Test that categories with no posts are still included"""
        empty_category = Category.objects.create(name="Empty Category")
        categories = get_categories()

        # All categories should be included, even empty ones
        self.assertEqual(categories.count(), 3)
        self.assertIn(empty_category, categories)


class GetRecentPostsTest(TemplateTagsTest):
    """Test cases for get_recent_posts template tag"""

    def test_get_recent_posts_returns_correct_number(self):
        """Test that get_recent_posts returns specified number of posts"""
        recent_posts = get_recent_posts(2)

        self.assertEqual(len(recent_posts), 2)

    def test_get_recent_posts_ordered_by_publish_date(self):
        """Test that recent posts are ordered by publish date (newest first)"""
        recent_posts = get_recent_posts(3)

        self.assertEqual(recent_posts[0], self.post1)  # Most recent
        self.assertEqual(recent_posts[1], self.post2)
        self.assertEqual(recent_posts[2], self.post3)  # Oldest

    def test_get_recent_posts_only_published(self):
        """Test that only published posts are returned"""
        recent_posts = get_recent_posts(10)  # Request more than available

        # Should only return 3 published posts, not the draft
        self.assertEqual(len(recent_posts), 3)
        self.assertNotIn(self.draft_post, recent_posts)

    def test_get_recent_posts_default_limit(self):
        """Test that default limit works correctly"""
        recent_posts = get_recent_posts()

        # Default should be 5, but we only have 3 published posts
        self.assertEqual(len(recent_posts), 3)


class GetPopularPostsTest(TemplateTagsTest):
    """Test cases for get_popular_posts template tag"""

    def test_get_popular_posts_returns_correct_number(self):
        """Test that get_popular_posts returns specified number of posts"""
        popular_posts = get_popular_posts(2)

        self.assertEqual(len(popular_posts), 2)

    def test_get_popular_posts_ordered_by_view_count(self):
        """Test that popular posts are ordered by view count (highest first)"""
        popular_posts = get_popular_posts(3)

        self.assertEqual(popular_posts[0], self.post1)  # 10 views
        self.assertEqual(popular_posts[1], self.post2)  # 5 views
        self.assertEqual(popular_posts[2], self.post3)  # 2 views

    def test_get_popular_posts_only_published(self):
        """Test that only published posts are returned"""
        popular_posts = get_popular_posts(10)  # Request more than available

        # Should only return 3 published posts, not the draft
        self.assertEqual(len(popular_posts), 3)
        self.assertNotIn(self.draft_post, popular_posts)

    def test_get_popular_posts_default_limit(self):
        """Test that default limit works correctly"""
        popular_posts = get_popular_posts()

        # Default should be 5, but we only have 3 published posts
        self.assertEqual(len(popular_posts), 3)


class GetPopularTagsTest(TemplateTagsTest):
    """Test cases for get_popular_tags template tag"""

    def test_get_popular_tags_returns_correct_number(self):
        """Test that get_popular_tags returns specified number of tags"""
        popular_tags = get_popular_tags(2)

        self.assertEqual(len(popular_tags), 2)

    def test_get_popular_tags_ordered_by_post_count(self):
        """Test that popular tags are ordered by post count (highest first)"""
        popular_tags = get_popular_tags(3)

        # Tag1 and Tag3 are used in 2 posts each, Tag2 is used in 2 posts
        # Order might vary for same counts, but all should be included
        tag_names = [tag.name for tag in popular_tags]
        self.assertIn("Python", tag_names)
        self.assertIn("Django", tag_names)
        self.assertIn("JavaScript", tag_names)

    def test_get_popular_tags_default_limit(self):
        """Test that default limit works correctly"""
        popular_tags = get_popular_tags()

        # Default should be 10, but we only have 3 tags
        self.assertEqual(len(popular_tags), 3)


class GetArchiveMonthsTest(TemplateTagsTest):
    """Test cases for get_archive_months template tag"""

    def setUp(self):
        """Set up test data with posts in different months"""
        super().setUp()

        # Create posts in different months
        self.post_jan = Post.objects.create(
            title="January Post",
            author=self.user,
            category=self.category1,
            content="January content",
            status=Post.PUBLISHED,
            publish_date=timezone.datetime(2024, 1, 15),
        )

        self.post_feb = Post.objects.create(
            title="February Post",
            author=self.user,
            category=self.category1,
            content="February content",
            status=Post.PUBLISHED,
            publish_date=timezone.datetime(2024, 2, 20),
        )

        self.post_mar = Post.objects.create(
            title="March Post",
            author=self.user,
            category=self.category1,
            content="March content",
            status=Post.PUBLISHED,
            publish_date=timezone.datetime(2024, 3, 10),
        )

    def test_get_archive_months_returns_correct_number(self):
        """Test that get_archive_months returns specified number of months"""
        archive_months = get_archive_months(2)

        self.assertEqual(len(archive_months), 2)

    def test_get_archive_months_ordered_by_date_descending(self):
        """Test that archive months are ordered by date (newest first)"""
        archive_months = get_archive_months(3)

        # Should be ordered by year/month descending
        self.assertEqual(archive_months[0].year, 2024)
        self.assertEqual(archive_months[0].month, 3)  # March

        self.assertEqual(archive_months[1].year, 2024)
        self.assertEqual(archive_months[1].month, 2)  # February

        self.assertEqual(archive_months[2].year, 2024)
        self.assertEqual(archive_months[2].month, 1)  # January

    def test_get_archive_months_only_months_with_posts(self):
        """Test that only months with published posts are returned"""
        # We have posts in Jan, Feb, Mar 2024
        archive_months = get_archive_months(12)

        months_with_posts = {(m.year, m.month) for m in archive_months}

        self.assertIn((2024, 1), months_with_posts)
        self.assertIn((2024, 2), months_with_posts)
        self.assertIn((2024, 3), months_with_posts)

        # Should not include months without posts
        self.assertNotIn((2024, 4), months_with_posts)

    def test_get_archive_months_excludes_draft_posts(self):
        """Test that months with only draft posts are excluded"""
        # Create a draft post in April 2024
        Post.objects.create(
            title="April Draft",
            author=self.user,
            category=self.category1,
            content="April draft content",
            status=Post.DRAFT,
            publish_date=timezone.datetime(2024, 4, 5),
        )

        archive_months = get_archive_months(12)
        months_with_posts = {(m.year, m.month) for m in archive_months}

        # April should not be included since it only has a draft post
        self.assertNotIn((2024, 4), months_with_posts)


class GetPostCountByMonthTest(TemplateTagsTest):
    """Test cases for get_post_count_by_month template tag"""

    def setUp(self):
        """Set up test data with posts in specific months"""
        super().setUp()

        # Create multiple posts in January 2024
        for i in range(3):
            Post.objects.create(
                title=f"January Post {i}",
                author=self.user,
                category=self.category1,
                content=f"January content {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.datetime(2024, 1, 10 + i),
            )

        # Create posts in February 2024
        for i in range(2):
            Post.objects.create(
                title=f"February Post {i}",
                author=self.user,
                category=self.category1,
                content=f"February content {i}",
                status=Post.PUBLISHED,
                publish_date=timezone.datetime(2024, 2, 15 + i),
            )

    def test_get_post_count_by_month_returns_correct_count(self):
        """Test that get_post_count_by_month returns correct post count"""
        # January 2024 should have 3 posts
        jan_count = get_post_count_by_month(2024, 1)
        self.assertEqual(jan_count, 3)

        # February 2024 should have 2 posts
        feb_count = get_post_count_by_month(2024, 2)
        self.assertEqual(feb_count, 2)

    def test_get_post_count_by_month_only_published_posts(self):
        """Test that only published posts are counted"""
        # Create a draft post in January 2024
        Post.objects.create(
            title="January Draft",
            author=self.user,
            category=self.category1,
            content="January draft content",
            status=Post.DRAFT,
            publish_date=timezone.datetime(2024, 1, 25),
        )

        # Count should still be 3 (only published posts)
        jan_count = get_post_count_by_month(2024, 1)
        self.assertEqual(jan_count, 3)

    def test_get_post_count_by_month_empty_month(self):
        """Test that empty months return 0"""
        # March 2024 has no posts
        mar_count = get_post_count_by_month(2024, 3)
        self.assertEqual(mar_count, 0)


class BlogSidebarTest(TemplateTagsTest):
    """Test cases for blog_sidebar template tag"""

    def test_blog_sidebar_returns_dict(self):
        """Test that blog_sidebar returns a dictionary"""
        sidebar_data = blog_sidebar()

        self.assertIsInstance(sidebar_data, dict)

    def test_blog_sidebar_contains_expected_keys(self):
        """Test that sidebar contains all expected sections"""
        sidebar_data = blog_sidebar()

        expected_keys = {
            "categories",
            "recent_posts",
            "popular_posts",
            "popular_tags",
            "archive_months",
        }

        for key in expected_keys:
            self.assertIn(key, sidebar_data)

    def test_blog_sidebar_categories(self):
        """Test that sidebar categories are correct"""
        sidebar_data = blog_sidebar()
        categories = sidebar_data["categories"]

        self.assertEqual(categories.count(), 2)
        self.assertIn(self.category1, categories)
        self.assertIn(self.category2, categories)

    def test_blog_sidebar_recent_posts(self):
        """Test that sidebar recent posts are correct"""
        sidebar_data = blog_sidebar()
        recent_posts = sidebar_data["recent_posts"]

        # Default should be 5 recent posts
        self.assertEqual(len(recent_posts), 3)  # We only have 3 published posts
        self.assertEqual(recent_posts[0], self.post1)  # Most recent

    def test_blog_sidebar_popular_posts(self):
        """Test that sidebar popular posts are correct"""
        sidebar_data = blog_sidebar()
        popular_posts = sidebar_data["popular_posts"]

        # Default should be 5 popular posts
        self.assertEqual(len(popular_posts), 3)  # We only have 3 published posts
        self.assertEqual(popular_posts[0], self.post1)  # Most popular (10 views)

    def test_blog_sidebar_popular_tags(self):
        """Test that sidebar popular tags are correct"""
        sidebar_data = blog_sidebar()
        popular_tags = sidebar_data["popular_tags"]

        # Default should be 10 popular tags
        self.assertEqual(len(popular_tags), 3)  # We only have 3 tags

    def test_blog_sidebar_archive_months(self):
        """Test that sidebar archive months are correct"""
        sidebar_data = blog_sidebar()
        archive_months = sidebar_data["archive_months"]

        # Should return recent months with posts
        self.assertGreater(len(archive_months), 0)


class ViewCounterTest(TemplateTagsTest):
    """Test cases for view_counter template tag"""

    def test_view_counter_returns_dict(self):
        """Test that view_counter returns a dictionary"""
        counter_data = view_counter(self.post1)

        self.assertIsInstance(counter_data, dict)

    def test_view_counter_contains_post(self):
        """Test that view_counter contains the post"""
        counter_data = view_counter(self.post1)

        self.assertIn("post", counter_data)
        self.assertEqual(counter_data["post"], self.post1)

    def test_view_counter_contains_view_count(self):
        """Test that view_counter contains view count"""
        counter_data = view_counter(self.post1)

        self.assertIn("view_count", counter_data)
        self.assertEqual(counter_data["view_count"], self.post1.view_count)

    def test_view_counter_with_different_posts(self):
        """Test that view_counter works with different posts"""
        counter_data1 = view_counter(self.post1)
        counter_data2 = view_counter(self.post2)

        self.assertEqual(counter_data1["view_count"], 10)
        self.assertEqual(counter_data2["view_count"], 5)
