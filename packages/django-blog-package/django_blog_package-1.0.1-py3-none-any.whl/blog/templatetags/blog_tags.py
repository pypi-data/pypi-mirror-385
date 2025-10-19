from django import template
from django.db.models import Count
from django.utils import timezone
from ..models import Category, Tag, Post, PostView

register = template.Library()


@register.simple_tag
def get_categories():
    """Get all categories with published post count"""
    return Category.objects.with_post_count()


@register.simple_tag
def get_recent_posts(limit=5):
    """Get recent published posts"""
    return Post.objects.published().select_related("author", "category")[:limit]


@register.simple_tag
def get_popular_tags(limit=10):
    """Get most popular tags by post count"""
    return Tag.objects.popular(limit=limit)


@register.simple_tag
def get_archive_months(limit=12):
    """Get archive months with post counts"""
    return Post.objects.published().dates("publish_date", "month", order="DESC")[:limit]


@register.simple_tag
def get_post_count_by_month(year, month):
    """Get post count for specific month"""
    return (
        Post.objects.published()
        .filter(publish_date__year=year, publish_date__month=month)
        .count()
    )


@register.simple_tag
def get_featured_posts(limit=3):
    """Get featured posts (could be extended with featured field)"""
    return Post.objects.published().select_related("author", "category")[:limit]


@register.simple_tag
def get_view_count(post):
    """Get view count for a post"""
    return post.view_count


@register.simple_tag
def get_popular_posts(limit=5):
    """Get most popular posts by view count"""
    return Post.objects.published().order_by("-view_count")[:limit]


@register.simple_tag
def get_trending_posts(limit=5):
    """Get trending posts (recent posts with high view counts)"""
    return (
        Post.objects.published()
        .filter(publish_date__gte=timezone.now() - timezone.timedelta(days=7))
        .order_by("-view_count")[:limit]
    )


@register.simple_tag
def get_unique_views_today(post):
    """Get unique views for a post today"""
    today = timezone.now().date()
    return PostView.objects.filter(post=post, created_at__date=today).count()


@register.simple_tag(takes_context=True)
def get_blog_settings(context):
    """Get blog settings from context or defaults"""
    from django.conf import settings

    return getattr(settings, "BLOG_SETTINGS", {})


@register.filter
def markdown(value):
    """Convert markdown to HTML"""
    try:
        import markdown

        return markdown.markdown(value)
    except ImportError:
        return value


@register.filter
def truncate_words(value, num_words):
    """Truncate text to specified number of words"""
    words = value.split()
    if len(words) <= num_words:
        return value
    return " ".join(words[:num_words]) + "..."


@register.filter
def truncate_chars(value, num_chars):
    """Truncate text to specified number of characters"""
    if len(value) <= num_chars:
        return value
    return value[:num_chars] + "..."


@register.filter
def reading_time(value, words_per_minute=200):
    """Calculate reading time in minutes"""
    word_count = len(value.split())
    minutes = word_count / words_per_minute
    return max(1, round(minutes))


@register.simple_tag
def get_comment_count(post):
    """Get approved comment count for a post"""
    return post.comments.approved().count()


@register.simple_tag
def get_related_posts(post, limit=3):
    """Get related posts by category and tags"""
    return (
        Post.objects.published()
        .filter(category=post.category)
        .exclude(pk=post.pk)
        .prefetch_related("tags")[:limit]
    )


@register.inclusion_tag("blog/includes/sidebar.html")
def blog_sidebar():
    """Render blog sidebar with common elements"""
    return {
        "categories": get_categories(),
        "recent_posts": get_recent_posts(),
        "popular_posts": get_popular_posts(),
        "trending_posts": get_trending_posts(),
        "popular_tags": get_popular_tags(),
        "archive_months": get_archive_months(),
    }


@register.inclusion_tag("blog/includes/pagination.html")
def blog_pagination(page_obj, paginator, request):
    """Render pagination controls"""
    return {
        "page_obj": page_obj,
        "paginator": paginator,
        "request": request,
    }


@register.inclusion_tag("blog/includes/view_counter.html")
def view_counter(post):
    """Render view counter badge"""
    return {"post": post, "view_count": post.view_count}


@register.inclusion_tag("blog/includes/view_stats.html")
def view_stats(post):
    """Render detailed view statistics"""
    today_views = get_unique_views_today(post)
    return {
        "post": post,
        "total_views": post.view_count,
        "today_views": today_views,
    }


@register.inclusion_tag("blog/includes/social_sharing.html")
def social_sharing_buttons(post, platforms=None):
    """Render social sharing buttons"""
    if platforms is None:
        platforms = ["twitter", "facebook", "linkedin"]

    return {
        "post": post,
        "platforms": platforms,
    }


@register.simple_tag
def get_next_post(post):
    """Get next post in chronological order"""
    try:
        return (
            Post.objects.published()
            .filter(publish_date__gt=post.publish_date)
            .order_by("publish_date")
            .first()
        )
    except Post.DoesNotExist:
        return None


@register.simple_tag
def get_previous_post(post):
    """Get previous post in chronological order"""
    try:
        return (
            Post.objects.published()
            .filter(publish_date__lt=post.publish_date)
            .order_by("-publish_date")
            .first()
        )
    except Post.DoesNotExist:
        return None


@register.filter
def format_date(value, format_string="F j, Y"):
    """Format date using Django's date filter with default format"""
    from django.template.defaultfilters import date

    return date(value, format_string)


@register.simple_tag
def get_post_years():
    """Get distinct years with published posts"""
    return Post.objects.published().dates("publish_date", "year", order="DESC")
