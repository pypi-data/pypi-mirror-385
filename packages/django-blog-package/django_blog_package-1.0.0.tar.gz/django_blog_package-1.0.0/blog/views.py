from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    ArchiveIndexView,
    YearArchiveView,
    MonthArchiveView,
)
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404

from .models import Post, Category, Tag, Comment
from .forms import CommentForm


class PostListView(ListView):
    """View for displaying list of published blog posts"""

    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Return only published posts ordered by publish date"""
        return (
            Post.objects.published()
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        """Add additional context data for the template"""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Latest Posts"
        return context


class PostDetailView(DetailView):
    """View for displaying individual blog post"""

    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        """Return only published posts"""
        return (
            Post.objects.published()
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_object(self, queryset=None):
        """Get post object using year, month, day, and slug"""
        if queryset is None:
            queryset = self.get_queryset()

        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        day = self.kwargs.get("day")
        slug = self.kwargs.get("slug")

        if not all([year, month, day, slug]):
            raise Http404("Invalid URL parameters")

        # Filter by date components and slug
        queryset = queryset.filter(
            publish_date__year=year,
            publish_date__month=month,
            publish_date__day=day,
            slug=slug,
        )

        obj = get_object_or_404(queryset)
        return obj

    def get_context_data(self, **kwargs):
        """Add comment form and approved comments to context"""
        context = super().get_context_data(**kwargs)
        post = self.object

        # Add comment form
        context["comment_form"] = CommentForm()

        # Add approved comments for this post
        context["comments"] = post.comments.approved().select_related("parent")

        # Add related posts (same category, excluding current post)
        context["related_posts"] = (
            Post.objects.published()
            .filter(category=post.category)
            .exclude(pk=post.pk)[:5]
        )

        # Add view count to context
        context["view_count"] = post.view_count

        return context


class CategoryPostListView(PostListView):
    """View for displaying posts by category"""

    def get_queryset(self):
        """Return published posts filtered by category slug"""
        category_slug = self.kwargs.get("slug")
        self.category = get_object_or_404(Category, slug=category_slug)
        return (
            Post.objects.by_category(category_slug)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        """Add category to context"""
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["page_title"] = f"Posts in {self.category.name}"
        return context


class TagPostListView(PostListView):
    """View for displaying posts by tag"""

    def get_queryset(self):
        """Return published posts filtered by tag slug"""
        tag_slug = self.kwargs.get("slug")
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        return (
            Post.objects.by_tag(tag_slug)
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        """Add tag to context"""
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        context["page_title"] = f"Posts tagged with {self.tag.name}"
        return context


class PostSearchView(ListView):
    """View for searching blog posts"""

    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Return search results based on query"""
        query = self.request.GET.get("q", "").strip()

        if not query:
            return Post.objects.none()

        # Search in title, content, excerpt, and tags
        return (
            Post.objects.published()
            .filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query)
                | Q(tags__name__icontains=query)
            )
            .distinct()
            .select_related("author", "category")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        """Add search query to context"""
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        context["search_query"] = query
        context["page_title"] = f'Search Results for "{query}"' if query else "Search"
        return context


class PostArchiveView(ArchiveIndexView):
    """View for displaying post archive"""

    model = Post
    date_field = "publish_date"
    template_name = "blog/post_archive.html"
    context_object_name = "posts"
    paginate_by = 20

    def get_queryset(self):
        """Return published posts for archive"""
        return Post.objects.published().select_related("author", "category")


class YearArchiveView(YearArchiveView):
    """View for displaying posts by year"""

    model = Post
    date_field = "publish_date"
    template_name = "blog/post_archive.html"
    context_object_name = "posts"
    make_object_list = True

    def get_queryset(self):
        """Return published posts for the year"""
        return Post.objects.published().select_related("author", "category")


class MonthArchiveView(MonthArchiveView):
    """View for displaying posts by month"""

    model = Post
    date_field = "publish_date"
    template_name = "blog/post_archive.html"
    context_object_name = "posts"
    month_format = "%m"

    def get_queryset(self):
        """Return published posts for the month"""
        return Post.objects.published().select_related("author", "category")


def add_comment(request, post_id):
    """View for handling comment submission"""
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post

            # If user is authenticated, use their info
            if request.user.is_authenticated:
                comment.author_name = (
                    request.user.get_full_name() or request.user.username
                )
                comment.author_email = request.user.email

            # Auto-approve comments from authenticated users
            if request.user.is_authenticated:
                comment.is_approved = True

            comment.save()

            if comment.is_approved:
                messages.success(request, "Your comment has been posted successfully!")
            else:
                messages.success(
                    request,
                    "Your comment has been submitted and is awaiting moderation.",
                )

            return redirect(post.get_absolute_url() + "#comments")
    else:
        form = CommentForm()

    # If GET request or invalid form, redirect back to post
    return redirect(post.get_absolute_url())
