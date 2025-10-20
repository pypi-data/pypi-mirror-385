# Django Blog Package

> **Important Documentation**: After installation, see the included documentation files for setup instructions:
> - `CKEDITOR_SETUP.md` - Complete CKEditor setup guide
> - `CKEDITOR_TROUBLESHOOTING.md` - CKEditor issues and solutions
> - `CKEDITOR_SETTINGS_TEMPLATE.py` - Ready-to-copy CKEditor configuration
> - `check_ckeditor_config.py` - CKEditor configuration verification script
> - `VIEW_COUNTER_SETUP.md` - Complete view counter middleware setup guide

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

2. Add to your Django project's `INSTALLED_APPS` (CKEditor must be added BEFORE the blog app):
```python
INSTALLED_APPS = [
    # ...
    'ckeditor',
    'ckeditor_uploader',  # Optional, for file uploads
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

## CKEditor Configuration

**Important**: The blog package requires CKEditor configuration in your project's settings. You MUST add the configuration to your `settings.py` file.

**Documentation Location**: After installation, you'll find these documentation files in your package directory:
- `CKEDITOR_SETUP.md` - Complete setup guide with step-by-step instructions
- `CKEDITOR_TROUBLESHOOTING.md` - Solutions for common errors
- `CKEDITOR_SETTINGS_TEMPLATE.py` - Ready-to-copy configuration template
- `check_ckeditor_config.py` - Script to verify your configuration

**Quick Configuration**: Add the following to your `settings.py` file:

```python
# Media configuration (required for file uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# CKEditor configuration for blog posts
CKEDITOR_CONFIGS = {
    'blog_editor': {
        'toolbar': 'Full',
        'height': 500,
        'width': '100%',
        'extraPlugins': 'codesnippet,image2,uploadimage,find,autolink,autoembed,embedsemantic,autogrow',
        'removePlugins': 'elementspath',
        'resize_enabled': True,
        'allowedContent': True,
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserUploadMethod': 'form',
        'autoGrow_minHeight': 400,
        'autoGrow_maxHeight': 1200,
        'autoGrow_bottomSpace': 50,
        'autoGrow_onStartup': True,
        'wordcount': {
            'showParagraphs': True,
            'showWordCount': True,
            'showCharCount': True,
            'countSpacesAsChars': True,
            'countHTML': False,
        },
        'linkDefaultTarget': '_blank',
        'find_highlight': {
            'element': 'span',
            'styles': {'background-color': '#ffeb3b', 'color': '#000000'}
        },
        'scayt_autoStartup': True,
        'scayt_sLang': 'en_US',
        'scayt_maxSuggestions': 5,
        'scayt_minWordLength': 4,
    }
}
```

For the complete configuration including the full toolbar setup, see the included `CKEDITOR_SETUP.md` file that comes with the package.

3. Add CKEditor URLs to your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ... your other URL patterns
    path('ckeditor/', include('ckeditor_uploader.urls')),
]
```

## Configuration

### View Counter Middleware

For complete setup instructions, see [VIEW_COUNTER_SETUP.md](VIEW_COUNTER_SETUP.md).

The blog package includes a sophisticated view counter that tracks unique post views. To enable it, add the middleware to your Django settings:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'blog.middleware.view_counter.ViewCounterMiddleware',
    'blog.middleware.view_counter.ViewCounterCleanupMiddleware',
    # ... other middleware
]
```

**Features:**
- **Unique View Tracking**: Counts each user only once per post (IP + session based)
- **Duplicate Prevention**: Prevents counting the same user multiple times
- **Automatic Cleanup**: Removes old view records after 30 days
- **Performance Optimized**: Uses caching to minimize database impact

**How it works:**
- Automatically tracks views when users visit post detail pages
- Uses IP address, session key, and user agent for unique identification
- Prevents duplicate counts for the same user within 1 hour
- Cleanup runs once per day to remove old records

**Displaying View Counts:**
View counts are automatically available on Post objects and in templates:

```django
{# In templates #}
{{ post.view_count }} views

{# In views #}
post.view_count
```

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
- django-ckeditor >= 6.0, < 7.0 (for rich text editing)

## CKEditor Support

This package includes full CKEditor integration for rich text editing:

- **Rich Text Content**: Blog posts use CKEditor's RichTextField
- **Admin Integration**: CKEditor widgets automatically configured in Django admin
- **File Uploads**: Support for image and file uploads (when configured)
- **Document Search & Replace**: Find (Ctrl+F) and replace text throughout documents
- **Spell Checking**: Real-time spell checking as you type
- **Auto-Grow Editor**: Editor expands automatically with content
- **Advanced Formatting**: Tables, fonts, colors, and special characters

For detailed CKEditor setup and configuration, see the included `CKEDITOR_SETUP.md` file that comes with the package installation.

**Troubleshooting**: If you encounter "No configuration named 'blog_editor' found" errors:

1. **Check the included documentation**: See `CKEDITOR_TROUBLESHOOTING.md` for detailed solutions
2. **Run the verification script**: Use `check_ckeditor_config.py` to diagnose issues
3. **Ensure configuration**: 
   - `ckeditor` is in INSTALLED_APPS before `blog`
   - `CKEDITOR_CONFIGS` with `blog_editor` configuration is added to your `settings.py`
   - `MEDIA_URL` and `MEDIA_ROOT` are configured
   - CKEditor URLs are added to your `urls.py`

## View Counter Not Working?

If the view counter isn't tracking views in your project, see the complete troubleshooting guide in [VIEW_COUNTER_SETUP.md](VIEW_COUNTER_SETUP.md).

Quick fixes:
1. **Check Middleware Order**: Ensure the view counter middleware is added to `MIDDLEWARE` in your `settings.py`
2. **Verify Session Middleware**: Django's session middleware must be enabled for proper tracking
3. **Check URLs**: The view counter only works with the built-in `PostDetailView` URLs
4. **Enable Debug Mode**: Check Django logs for any middleware errors

**Required Middleware Order:**
```python
MIDDLEWARE = [
    # ... other middleware
    'django.contrib.sessions.middleware.SessionMiddleware',  # Required for sessions
    # ... other middleware
    'blog.middleware.view_counter.ViewCounterMiddleware',
    'blog.middleware.view_counter.ViewCounterCleanupMiddleware',
    # ... other middleware
]
```

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