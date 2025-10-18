from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""

    list_display = ["name", "slug", "post_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Posts"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model"""

    list_display = ["name", "slug", "post_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at"]

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = "Posts"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin interface for Post model"""

    list_display = [
        "title",
        "author",
        "category",
        "status",
        "publish_date",
        "is_published",
        "comment_count",
        "created_at",
    ]
    list_filter = ["status", "category", "tags", "publish_date", "created_at"]
    search_fields = ["title", "content", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ["tags"]
    date_hierarchy = "publish_date"
    readonly_fields = ["created_at", "updated_at", "preview_link"]
    fieldsets = (
        (
            "Content",
            {"fields": ("title", "slug", "content", "excerpt", "featured_image")},
        ),
        ("Metadata", {"fields": ("author", "category", "tags", "meta_description")}),
        ("Publication", {"fields": ("status", "publish_date")}),
        (
            "System",
            {
                "fields": ("created_at", "updated_at", "preview_link"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["make_published", "make_draft", "update_publish_date"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author", "category")

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Comments"

    def is_published(self, obj):
        return obj.is_published()

    is_published.boolean = True
    is_published.short_description = "Published"

    def preview_link(self, obj):
        if obj.pk and obj.is_published():
            return format_html(
                '<a href="{}" target="_blank">View post</a>', obj.get_absolute_url()
            )
        return "Not available (draft or no publish date)"

    preview_link.short_description = "Preview"

    def make_published(self, request, queryset):
        """Admin action to mark selected posts as published"""
        updated = queryset.update(status=Post.PUBLISHED, publish_date=timezone.now())
        self.message_user(request, f"Successfully published {updated} post(s).")

    make_published.short_description = "Mark selected posts as published"

    def make_draft(self, request, queryset):
        """Admin action to mark selected posts as draft"""
        updated = queryset.update(status=Post.DRAFT)
        self.message_user(request, f"Successfully marked {updated} post(s) as draft.")

    make_draft.short_description = "Mark selected posts as draft"

    def update_publish_date(self, request, queryset):
        """Admin action to update publish date to current time"""
        updated = queryset.update(publish_date=timezone.now())
        self.message_user(
            request, f"Successfully updated publish date for {updated} post(s)."
        )

    update_publish_date.short_description = "Update publish date to now"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin interface for Comment model"""

    list_display = [
        "author_name",
        "post_title",
        "is_approved",
        "is_reply",
        "created_at",
        "content_preview",
    ]
    list_filter = ["is_approved", "created_at", "post__category"]
    search_fields = ["author_name", "author_email", "content", "post__title"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["approve_comments", "disapprove_comments", "mark_as_spam"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("post", "parent")

    def post_title(self, obj):
        return obj.post.title

    post_title.short_description = "Post"
    post_title.admin_order_field = "post__title"

    def is_reply(self, obj):
        return obj.is_reply()

    is_reply.boolean = True
    is_reply.short_description = "Is Reply"

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content Preview"

    def approve_comments(self, request, queryset):
        """Admin action to approve selected comments"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Successfully approved {updated} comment(s).")

    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        """Admin action to disapprove selected comments"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Successfully disapproved {updated} comment(s).")

    disapprove_comments.short_description = "Disapprove selected comments"

    def mark_as_spam(self, request, queryset):
        """Admin action to mark comments as spam (delete them)"""
        count, _ = queryset.delete()
        self.message_user(request, f"Successfully deleted {count} spam comment(s).")

    mark_as_spam.short_description = "Mark selected comments as spam (delete)"
