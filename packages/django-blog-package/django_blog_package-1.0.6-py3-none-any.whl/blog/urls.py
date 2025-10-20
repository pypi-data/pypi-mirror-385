from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Post list views
    path("", views.PostListView.as_view(), name="post_list"),
    path("page/<int:page>/", views.PostListView.as_view(), name="post_list_paginated"),
    # Category and tag views
    path(
        "category/<slug:slug>/",
        views.CategoryPostListView.as_view(),
        name="category_posts",
    ),
    path("tag/<slug:slug>/", views.TagPostListView.as_view(), name="tag_posts"),
    # Search
    path("search/", views.PostSearchView.as_view(), name="post_search"),
    # Post detail with date-based URL
    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    # Comment submission
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
    # Archive views
    path("archive/", views.PostArchiveView.as_view(), name="post_archive"),
    path("archive/<int:year>/", views.YearArchiveView.as_view(), name="year_archive"),
    path(
        "archive/<int:year>/<int:month>/",
        views.MonthArchiveView.as_view(),
        name="month_archive",
    ),
]
