from django import forms
from django.utils import timezone
from .models import Comment, Post


class CommentForm(forms.ModelForm):
    """Form for submitting comments on blog posts"""

    class Meta:
        model = Comment
        fields = ["author_name", "author_email", "author_website", "content"]
        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Name",
                    "required": True,
                }
            ),
            "author_email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Email",
                    "required": True,
                }
            ),
            "author_website": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your Website (optional)",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Your comment...",
                    "rows": 4,
                    "required": True,
                }
            ),
        }
        labels = {
            "author_name": "Name",
            "author_email": "Email",
            "author_website": "Website",
            "content": "Comment",
        }

    def clean_content(self):
        """Validate comment content"""
        content = self.cleaned_data.get("content", "").strip()
        if len(content) < 10:
            raise forms.ValidationError("Comment must be at least 10 characters long.")
        if len(content) > 1000:
            raise forms.ValidationError("Comment cannot exceed 1000 characters.")
        return content

    def clean_author_name(self):
        """Validate author name"""
        name = self.cleaned_data.get("author_name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Name must be at least 2 characters long.")
        if len(name) > 100:
            raise forms.ValidationError("Name cannot exceed 100 characters.")
        return name


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts"""

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "content",
            "excerpt",
            "category",
            "tags",
            "featured_image",
            "status",
            "publish_date",
            "meta_description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Post Title"}
            ),
            "slug": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "url-slug"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 15,
                    "placeholder": "Post content...",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Brief summary of the post...",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "publish_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
            "meta_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meta description for SEO...",
                }
            ),
        }
        help_texts = {
            "slug": "URL-friendly version of the title. Auto-generated if left empty.",
            "excerpt": "Brief summary that will appear in post listings.",
            "meta_description": "Meta description for SEO. Auto-generated from excerpt if left empty.",
        }

    def clean_slug(self):
        """Validate and generate slug if empty"""
        slug = self.cleaned_data.get("slug", "").strip()
        if not slug and self.cleaned_data.get("title"):
            from django.utils.text import slugify

            slug = slugify(self.cleaned_data["title"])
        return slug

    def clean_publish_date(self):
        """Validate publish date"""
        publish_date = self.cleaned_data.get("publish_date")
        if publish_date and publish_date < timezone.now():
            raise forms.ValidationError("Publish date cannot be in the past.")
        return publish_date


class SearchForm(forms.Form):
    """Form for searching blog posts"""

    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search posts...",
                "aria-label": "Search",
            }
        ),
        label="",
    )

    def clean_q(self):
        """Validate search query"""
        query = self.cleaned_data.get("q", "").strip()
        if query and len(query) < 2:
            raise forms.ValidationError(
                "Search query must be at least 2 characters long."
            )
        return query
