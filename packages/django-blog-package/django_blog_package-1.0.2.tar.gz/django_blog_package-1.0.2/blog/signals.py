from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from .models import Post, Category, Tag


@receiver(pre_save, sender=Post)
def update_post_meta(sender, instance, **kwargs):
    """Update post metadata before saving"""

    # Auto-generate slug if not provided
    if not instance.slug and instance.title:
        instance.slug = slugify(instance.title)

    # Auto-generate excerpt if not provided
    if not instance.excerpt and instance.content:
        instance.excerpt = (
            instance.content[:150] + "..."
            if len(instance.content) > 150
            else instance.content
        )

    # Auto-generate meta description if not provided
    if not instance.meta_description:
        instance.meta_description = instance.excerpt[:160]

    # Set publish date when status changes to published
    if instance.status == Post.PUBLISHED and not instance.publish_date:
        instance.publish_date = timezone.now()


@receiver(pre_save, sender=Category)
def update_category_slug(sender, instance, **kwargs):
    """Update category slug before saving"""
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Tag)
def update_tag_slug(sender, instance, **kwargs):
    """Update tag slug before saving"""
    if not instance.slug and instance.name:
        instance.slug = slugify(instance.name)


@receiver(post_save, sender=Post)
def handle_post_publication(sender, instance, created, **kwargs):
    """Handle actions after a post is saved"""

    # If this is a newly published post, you could send notifications here
    if instance.is_published() and created:
        # Placeholder for future notification functionality
        # Example: send_email_notifications(instance)
        pass


@receiver(post_save, sender=Post)
def update_category_post_count(sender, instance, **kwargs):
    """Update category post count cache if needed"""
    # This could be used to maintain denormalized counts
    # Currently handled by managers, but kept for future use
    pass


@receiver(post_save, sender=Post)
def update_tag_post_count(sender, instance, **kwargs):
    """Update tag post count cache if needed"""
    # This could be used to maintain denormalized counts
    # Currently handled by managers, but kept for future use
    pass
