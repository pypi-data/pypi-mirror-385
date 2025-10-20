import hashlib
import time
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.conf import settings
from ..models import Post, PostView


class ViewCounterMiddleware(MiddlewareMixin):
    """Middleware to track unique post views for blog posts"""

    def process_response(self, request, response):
        """
        Track unique post views after response is processed
        Only track successful responses to PostDetailView
        """
        if response.status_code == 200 and hasattr(request, "resolver_match"):
            view_func = request.resolver_match.func
            view_class = getattr(view_func, "view_class", None)

            # Check if this is a PostDetailView
            if view_class and view_class.__name__ == "PostDetailView":
                # Get post from resolved view
                if hasattr(request, "resolver_match") and hasattr(
                    request.resolver_match, "kwargs"
                ):
                    post_slug = request.resolver_match.kwargs.get("slug")
                    year = request.resolver_match.kwargs.get("year")
                    month = request.resolver_match.kwargs.get("month")
                    day = request.resolver_match.kwargs.get("day")

                    if all([year, month, day, post_slug]):
                        self.track_view(request, year, month, day, post_slug)

        return response

    def track_view(self, request, year, month, day, slug):
        """Track unique view for a blog post"""
        try:
            # Get the post using the URL parameters
            post = Post.objects.published().get(
                publish_date__year=year,
                publish_date__month=month,
                publish_date__day=day,
                slug=slug,
            )

            # Generate unique identifier for this user/session
            user_identifier = self.get_user_identifier(request, post.pk)

            # Check cache first to avoid database hits for recent views
            cache_key = f"post_view_{post.pk}_{user_identifier}"
            if cache.get(cache_key):
                return  # Already tracked recently

            # Check if this view has already been counted in database
            client_ip = self.get_client_ip(request)
            session_key = request.session.session_key or ""

            view_exists = PostView.objects.filter(
                post=post,
                ip_address=client_ip,
                session_key=session_key,
            ).exists()

            if not view_exists:
                # Create new view record
                PostView.objects.create(
                    post=post,
                    ip_address=client_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[
                        :500
                    ],  # Limit length
                    session_key=session_key,
                    user=request.user if request.user.is_authenticated else None,
                )

                # Increment post view count
                post.view_count = PostView.objects.filter(post=post).count()
                post.save(update_fields=["view_count"])

                # Cache this view to prevent duplicate tracking for a while
                cache.set(cache_key, True, 3600)  # Cache for 1 hour

        except Post.DoesNotExist:
            # Post not found or not published, ignore
            pass
        except Exception as e:
            # Log error but don't break the request
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error tracking post view: {e}")

    def get_user_identifier(self, request, post_id):
        """Generate unique identifier for user tracking"""
        components = [
            self.get_client_ip(request),
            request.META.get("HTTP_USER_AGENT", "")[:100],  # Limit length
            request.session.session_key or "",
            str(post_id),
        ]

        # Add user ID if authenticated for better uniqueness
        if request.user.is_authenticated:
            components.append(str(request.user.pk))

        identifier_string = "|".join(components)
        return hashlib.md5(identifier_string.encode()).hexdigest()

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class ViewCounterCleanupMiddleware(MiddlewareMixin):
    """Middleware to periodically clean up old view records"""

    def process_request(self, request):
        """Check if we need to clean up old view records"""
        # Only run cleanup occasionally to avoid performance impact
        last_cleanup = cache.get("view_counter_last_cleanup")
        current_time = time.time()

        if (
            not last_cleanup or (current_time - last_cleanup) > 86400
        ):  # Run once per day
            self.cleanup_old_views()
            cache.set("view_counter_last_cleanup", current_time, 86400)

        return None

    def cleanup_old_views(self):
        """Remove view records older than 30 days"""
        try:
            from datetime import timedelta

            cutoff_date = timezone.now() - timedelta(days=30)

            old_views = PostView.objects.filter(created_at__lt=cutoff_date)
            count = old_views.count()
            old_views.delete()

            # Log cleanup for monitoring
            import logging

            logger = logging.getLogger(__name__)
            logger.info(f"Cleaned up {count} old post views")

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error cleaning up old post views: {e}")
