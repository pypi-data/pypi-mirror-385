from django.db import models
from django.utils import timezone
from django.db.models import Count, Q


class CategoryManager(models.Manager):
    """Custom manager for Category model"""

    def with_post_count(self):
        """Return categories annotated with published post count"""
        return (
            self.get_queryset()
            .annotate(
                published_posts_count=Count(
                    "posts",
                    filter=Q(posts__status="published")
                    & Q(posts__publish_date__lte=timezone.now()),
                )
            )
            .filter(published_posts_count__gt=0)
        )

    def active(self):
        """Return only categories that have published posts"""
        return self.with_post_count()


class TagManager(models.Manager):
    """Custom manager for Tag model"""

    def with_post_count(self):
        """Return tags annotated with published post count"""
        return self.get_queryset().annotate(
            published_posts_count=Count(
                "posts",
                filter=Q(posts__status="published")
                & Q(posts__publish_date__lte=timezone.now()),
            )
        )

    def popular(self, limit=10):
        """Return most popular tags by post count"""
        return (
            self.with_post_count()
            .filter(published_posts_count__gt=0)
            .order_by("-published_posts_count")[:limit]
        )

    def active(self):
        """Return only tags that have published posts"""
        return self.with_post_count().filter(published_posts_count__gt=0)


class CommentManager(models.Manager):
    """Custom manager for Comment model"""

    def approved(self):
        """Return only approved comments"""
        return self.get_queryset().filter(is_approved=True)

    def pending(self):
        """Return only pending comments awaiting moderation"""
        return self.get_queryset().filter(is_approved=False)

    def for_post(self, post):
        """Return comments for a specific post"""
        return self.get_queryset().filter(post=post)

    def top_level(self):
        """Return only top-level comments (not replies)"""
        return self.get_queryset().filter(parent__isnull=True)

    def with_replies(self):
        """Return comments with prefetched replies"""
        return self.get_queryset().prefetch_related("replies")
