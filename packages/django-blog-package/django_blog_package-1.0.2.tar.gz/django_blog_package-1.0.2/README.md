# Django Blog Package

A comprehensive, reusable Django blog package that can be easily installed and integrated into any Django project. This package provides a complete blogging system with standard features including post management, categories, tags, comments, user management, and enhanced rich text editing with CKEditor's full editor suite.

## Features

- **Easy Installation**: Simple pip installation and Django app configuration
- **Complete Blog Management**: Create, edit, publish, and manage blog posts
- **Categories & Tags**: Organize content with categories and flexible tagging
- **Comment System**: Threaded comments with moderation capabilities
- **Search Functionality**: Full-text search across posts, titles, and content
- **SEO Optimization**: Automatic meta tags, clean URLs, and SEO-friendly structure
- **Admin Interface**: Comprehensive Django admin integration
- **Customizable Templates**: Easy template overriding and theming
- **Social Sharing**: Built-in social media sharing buttons
- **Performance Optimized**: Efficient queries and caching support
- **Security**: Input validation, permission controls, and secure file uploads

## Quick Start

### Installation from PyPI

1. Install the package:
```bash
pip install django-blog-package
```

### Installation from Source

1. Clone the repository:
```bash
git clone https://github.com/josephbraide/django-blog-package.git
cd django-blog-package
```

2. Install the package:
```bash
pip install .
```

2. Add to your Django project's `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    'blog',
    # ...
]
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Include URLs in your project's `urls.py`:
```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('blog/', include('blog.urls')),
    # ...
]
```

5. Collect static files:
```bash
python manage.py collectstatic
```

## Configuration

### Basic Settings

Add the following to your `settings.py` for basic configuration:

```python
# Blog settings
BLOG_SETTINGS = {
    'PAGINATE_BY': 10,
    'COMMENTS_ENABLED': True,
    'COMMENT_MODERATION': True,
    'SEARCH_ENABLED': True,
    'SOCIAL_SHARING_ENABLED': True,
    'DEFAULT_CATEGORY_SLUG': 'general',
    'EXCERPT_LENGTH': 150,
    'IMAGE_UPLOAD_PATH': 'blog/images/',
    'ALLOW_HTML_IN_COMMENTS': False,
}
```

### URL Structure

The package provides the following URL patterns:

- `/blog/` - Blog post list
- `/blog/page/<page>/` - Paginated post list
- `/blog/search/` - Search results
- `/blog/category/<slug>/` - Posts by category
- `/blog/tag/<slug>/` - Posts by tag
- `/blog/<year>/<month>/<day>/<slug>/` - Individual post detail
- `/blog/comment/<post_id>/` - Comment submission
- `/blog/archive/` - Post archive
- `/blog/archive/<year>/` - Yearly archive
- `/blog/archive/<year>/<month>/` - Monthly archive

## Usage

### Creating Blog Posts

1. Access the Django admin at `/admin/`
2. Navigate to the Blog section
3. Create categories and tags as needed
4. Create blog posts with rich content

### Template Customization

Override default templates by creating your own templates in your project's template directory:

```bash
your_project/
├── templates/
│   └── blog/
│       ├── base.html
│       ├── post_list.html
│       ├── post_detail.html
│       ├── post_archive.html
│       └── includes/
│           ├── sidebar.html
│           ├── pagination.html
│           └── comments.html
```

### Template Tags

Use built-in template tags for common functionality:

```django
{% load blog_tags %}

{# Get categories #}
{% get_categories as categories %}

{# Get recent posts #}
{% get_recent_posts 5 as recent_posts %}

{# Get popular tags #}
{% get_popular_tags 10 as popular_tags %}

{# Render sidebar #}
{% blog_sidebar %}

{# Render pagination #}
{% blog_pagination page_obj paginator request %}

{# Social sharing buttons #}
{% social_sharing_buttons post %}
```

### Views and URLs

The package provides class-based views that can be extended:

```python
from blog.views import PostListView, PostDetailView

class CustomPostListView(PostListView):
    template_name = 'myapp/post_list.html'
    paginate_by = 15

class CustomPostDetailView(PostDetailView):
    template_name = 'myapp/post_detail.html'
```

## Models

### Core Models

- **Category**: Hierarchical organization of posts
- **Tag**: Flexible categorization through many-to-many relationships
- **Post**: Core content with publication workflow
- **Comment**: User engagement with moderation system

### Example Usage

```python
from blog.models import Post, Category, Tag

# Get published posts
published_posts = Post.objects.published()

# Get posts by category
tech_posts = Post.objects.by_category('technology')

# Get posts by tag
python_posts = Post.objects.by_tag('python')

# Get recent posts
recent_posts = Post.objects.recent(5)
```

## Admin Interface

The package provides a comprehensive admin interface with:

- Post management with bulk actions
- Category and tag management
- Comment moderation tools
- Publication workflow management
- Search and filtering capabilities

## Testing

Run the test suite:

```bash
python manage.py test blog
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## PyPI Deployment

To deploy a new version to PyPI:

1. Update the version in `setup.py`
2. Build the package:
```bash
python setup.py sdist bdist_wheel
```

3. Upload to PyPI:
```bash
twine upload dist/*
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

- Create an issue on GitHub
- Check the documentation
- Review the code examples

## Dependencies

- Django >= 4.2, < 5.0
- Pillow >= 9.0, < 11.0

## Compatibility

- Python 3.8+
- Django 4.2+
- SQLite, PostgreSQL, MySQL databases

## Roadmap

- [ ] RSS/Atom feeds
- [ ] Email notifications
- [ ] Advanced search with Elasticsearch
- [ ] Multi-language support
- [ ] Image galleries
- [ ] Newsletter integration
- [ ] Analytics integration
- [ ] API endpoints
- [ ] GraphQL support

---

**Django Blog Package** - Making blogging in Django projects simple and powerful.