from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.utils.text import slugify
import uuid

from .managers import CategoryManager, TagManager, CommentManager


class Category(models.Model):
    """Blog post category for organizing posts"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(
        blank=True, help_text="Brief description of the category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:category_posts", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tag for categorizing blog posts"""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TagManager()

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("blog:tag_posts", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PostManager(models.Manager):
    """Custom manager for Post model with common queries"""

    def published(self):
        """Return only published posts"""
        return self.get_queryset().filter(
            status=Post.PUBLISHED, publish_date__lte=timezone.now()
        )

    def drafts(self):
        """Return only draft posts"""
        return self.get_queryset().filter(status=Post.DRAFT)

    def by_category(self, category_slug):
        """Return published posts by category slug"""
        return self.published().filter(category__slug=category_slug)

    def by_tag(self, tag_slug):
        """Return published posts by tag slug"""
        return self.published().filter(tags__slug=tag_slug)

    def recent(self, limit=5):
        """Return recent published posts"""
        return self.published()[:limit]


class Post(models.Model):
    """Blog post model"""

    DRAFT = "draft"
    PUBLISHED = "published"
    STATUS_CHOICES = [
        (DRAFT, "Draft"),
        (PUBLISHED, "Published"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date="publish_date")
    content = models.TextField(help_text="Main content of the blog post")
    excerpt = models.TextField(
        blank=True, help_text="Brief summary of the post (optional)"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="posts"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    featured_image = models.ImageField(
        upload_to="blog/images/%Y/%m/",
        blank=True,
        null=True,
        help_text="Featured image for the post",
    )
    publish_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the post should be published",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meta_description = models.CharField(
        max_length=160, blank=True, help_text="Meta description for SEO (optional)"
    )
    view_count = models.PositiveIntegerField(default=0, help_text="Unique view count")

    objects = PostManager()

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-publish_date"]
        indexes = [
            models.Index(fields=["-publish_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.publish_date:
            return reverse(
                "blog:post_detail",
                kwargs={
                    "year": self.publish_date.year,
                    "month": self.publish_date.month,
                    "day": self.publish_date.day,
                    "slug": self.slug,
                },
            )
        return reverse("blog:post_detail", kwargs={"pk": self.pk})

    def is_published(self):
        """Check if post is published and publish date has passed"""
        return (
            self.status == self.PUBLISHED
            and self.publish_date
            and self.publish_date <= timezone.now()
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        # Auto-generate excerpt if not provided
        if not self.excerpt and self.content:
            self.excerpt = (
                self.content[:150] + "..." if len(self.content) > 150 else self.content
            )

        # Auto-generate meta description if not provided
        if not self.meta_description:
            self.meta_description = self.excerpt[:160]

        # Set publish date when status changes to published
        if self.status == self.PUBLISHED and not self.publish_date:
            self.publish_date = timezone.now()

        super().save(*args, **kwargs)


class Comment(models.Model):
    """Comment model for blog posts"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    objects = CommentManager()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "is_approved"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.post.title}"

    def is_reply(self):
        """Check if this comment is a reply to another comment"""
        return self.parent is not None

    def get_replies(self):
        """Get all replies to this comment"""
        return self.replies.filter(is_approved=True)


class PostView(models.Model):
    """Model to track unique post views by users"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_views")
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Post View"
        verbose_name_plural = "Post Views"
        unique_together = ["post", "ip_address", "session_key"]
        indexes = [
            models.Index(fields=["post", "ip_address", "session_key"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"View of {self.post.title} by {self.ip_address}"
