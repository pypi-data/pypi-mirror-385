from django.conf import settings


class BlogSettings:
    """Configuration settings for the Django Blog package"""

    # Default settings
    DEFAULTS = {
        # General settings
        "PAGINATE_BY": 10,
        "COMMENTS_ENABLED": True,
        "COMMENT_MODERATION": True,
        "SEARCH_ENABLED": True,
        "SOCIAL_SHARING_ENABLED": True,
        # Content settings
        "DEFAULT_CATEGORY_SLUG": "general",
        "EXCERPT_LENGTH": 150,
        "IMAGE_UPLOAD_PATH": "blog/images/",
        "ALLOW_HTML_IN_COMMENTS": False,
        # Tailwind CSS settings
        "USE_TAILWIND_CSS": True,
        "TAILWIND_CDN_URL": "https://cdn.tailwindcss.com",
        "TAILWIND_CONFIG": {
            "theme": {
                "extend": {
                    "colors": {
                        "primary": {
                            "50": "#eff6ff",
                            "500": "#3b82f6",
                            "600": "#2563eb",
                            "700": "#1d4ed8",
                        }
                    },
                    "fontFamily": {
                        "sans": ["Inter", "system-ui", "sans-serif"],
                    },
                }
            }
        },
        # View counter settings
        "ENABLE_VIEW_COUNTER": True,
        "VIEW_COUNTER_SESSION_DURATION": 24,  # hours
        "VIEW_COUNTER_CACHE_TIMEOUT": 3600,  # seconds
        "VIEW_COUNTER_CLEANUP_DAYS": 30,
        # SEO settings
        "AUTO_GENERATE_META_DESCRIPTION": True,
        "AUTO_GENERATE_EXCERPT": True,
        "USE_CLEAN_URLS": True,
        # Template settings
        "BASE_TEMPLATE": "blog/base.html",
        "POST_LIST_TEMPLATE": "blog/post_list.html",
        "POST_DETAIL_TEMPLATE": "blog/post_detail.html",
        # Admin settings
        "ADMIN_LIST_PER_PAGE": 25,
        "ADMIN_SEARCH_FIELDS": ["title", "content"],
        # Performance settings
        "USE_CACHING": True,
        "CACHE_TIMEOUT": 300,  # seconds
        "USE_SELECT_RELATED": True,
        "USE_PREFETCH_RELATED": True,
    }

    def __init__(self, user_settings=None):
        self.user_settings = user_settings or {}

    def __getattr__(self, attr):
        if attr in self.DEFAULTS:
            try:
                # Check if user has set this value
                return self.user_settings[attr]
            except KeyError:
                # Fall back to defaults
                return self.DEFAULTS[attr]
        raise AttributeError(f"Invalid blog setting: '{attr}'")


def get_blog_settings():
    """Get blog settings from Django settings or use defaults"""
    user_settings = getattr(settings, "BLOG_SETTINGS", {})
    return BlogSettings(user_settings)


# Convenience function to access settings
blog_settings = get_blog_settings()
