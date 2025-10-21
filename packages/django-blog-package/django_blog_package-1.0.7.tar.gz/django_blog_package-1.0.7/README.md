# Django Blog Package

A comprehensive, reusable Django blog package that can be easily installed and integrated into any Django project. This package provides a complete blogging system with standard features including post management, categories, tags, comments, user management, enhanced rich text editing with CKEditor's full editor suite, and sophisticated view tracking.

## Features

- **Easy Installation**: Simple pip installation and Django app configuration
- **Complete Blog Management**: Create, edit, publish, and manage blog posts
- **Categories & Tags**: Organize content with categories and flexible tagging
- **Comment System**: Threaded comments with moderation capabilities
- **Search Functionality**: Full-text search across posts, titles, and content
- **SEO Optimization**: Automatic meta tags, clean URLs, and SEO-friendly structure
- **Admin Interface**: Comprehensive Django admin integration with CKEditor
- **Rich Text Editing**: Full CKEditor suite with search/replace, spell checking, and advanced formatting
- **View Counter**: Sophisticated unique view tracking with duplicate prevention
- **Customizable Templates**: Easy template overriding and theming
- **Header/Footer Swapping**: Seamlessly integrate with existing company/business headers and footers
- **Social Sharing**: Built-in social media sharing buttons
- **Performance Optimized**: Efficient queries and caching support
- **Security**: Input validation, permission controls, and secure file uploads

## Quick Start

### Installation

```bash
pip install django-blog-package
```

### Basic Setup

1. **Add to INSTALLED_APPS** (CKEditor must be added BEFORE the blog app):
```python
# settings.py
INSTALLED_APPS = [
    # ... other Django apps
    'ckeditor',
    'ckeditor_uploader',  # Optional, for file uploads
    'blog',
]
```

2. **Run migrations**:
```bash
python manage.py migrate
```

3. **Include URLs** in your project's `urls.py`:
```python
from django.urls import include, path

urlpatterns = [
    # ... your other URL patterns
    path('blog/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),  # For file uploads
]
```

4. **Collect static files**:
```bash
python manage.py collectstatic
```

## Essential Configuration

### CKEditor Setup (REQUIRED)

**IMPORTANT**: You MUST add CKEditor configuration to your project's `settings.py`:

```python
# settings.py

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

### View Counter Middleware Setup

To enable the sophisticated view counter, add the middleware to your settings:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    
    # Session middleware is REQUIRED for view counter
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # ... other middleware
    
    # Add these two middleware classes
    'blog.middleware.view_counter.ViewCounterMiddleware',
    'blog.middleware.view_counter.ViewCounterCleanupMiddleware',
    
    # ... other middleware
]
```

**View Counter Features:**
- ✅ Unique view tracking (IP + session based)
- ✅ Duplicate prevention (1-hour cache)
- ✅ Automatic cleanup (30-day retention)
- ✅ Performance optimized with caching

### Blog Settings

Configure basic blog behavior:

```python
# settings.py
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
    
    # Header/Footer Configuration
    'USE_CUSTOM_HEADER': False,  # Set to True to use custom header
    'USE_CUSTOM_FOOTER': False,  # Set to True to use custom footer
    'HEADER_TEMPLATE': 'blog/includes/header.html',  # Default header template
    'FOOTER_TEMPLATE': 'blog/includes/footer.html',  # Default footer template
    'CUSTOM_HEADER_TEMPLATE': None,  # Path to your custom header template
    'CUSTOM_FOOTER_TEMPLATE': None,  # Path to your custom footer template
}
```

## Enhanced CKEditor Features

The package includes a fully configured CKEditor with:

### 🛠️ Full Editor Suite
- Complete toolbar with all editing tools
- Advanced formatting options
- Table creation and editing
- Multiple font styles and sizes

### 🔍 Document Search & Replace
- **Find text (Ctrl+F)** - Search throughout your document
- **Replace text** - Find and replace repeated characters
- **Highlight search results** - Visual feedback for matches

### ✨ Advanced Functionality
- **Spell checking** as you type
- **Auto-grow editor** that expands with content
- **Code snippet support** with syntax highlighting
- **Image upload and management**
- **Enhanced word count and statistics**
- **File upload capabilities**

## Header/Footer Integration

Seamlessly integrate the blog with your existing company/business website design by swapping the default header and footer with your own templates.

### Basic Configuration

```python
# Use default blog header/footer (default behavior)
BLOG_SETTINGS = {
    'USE_CUSTOM_HEADER': False,
    'USE_CUSTOM_FOOTER': False,
}

# Use custom header only
BLOG_SETTINGS = {
    'USE_CUSTOM_HEADER': True,
    'USE_CUSTOM_FOOTER': False,
    'CUSTOM_HEADER_TEMPLATE': 'myapp/includes/header.html',
}

# Use custom footer only
BLOG_SETTINGS = {
    'USE_CUSTOM_HEADER': False,
    'USE_CUSTOM_FOOTER': True,
    'CUSTOM_FOOTER_TEMPLATE': 'myapp/includes/footer.html',
}

# Use both custom header and footer
BLOG_SETTINGS = {
    'USE_CUSTOM_HEADER': True,
    'USE_CUSTOM_FOOTER': True,
    'CUSTOM_HEADER_TEMPLATE': 'myapp/includes/header.html',
    'CUSTOM_FOOTER_TEMPLATE': 'myapp/includes/footer.html',
}
```

### Template Requirements

Your custom templates should include blog navigation links:

**Header Template:**
```html
<!-- myapp/templates/myapp/includes/header.html -->
<header class="your-company-header">
    <nav>
        <a href="/">Home</a>
        <a href="{% url 'blog:post_list' %}">Blog</a>
        <a href="{% url 'blog:post_archive' %}">Archive</a>
        <a href="{% url 'blog:post_search' %}">Search</a>
        <!-- Your other navigation items -->
    </nav>
</header>
```

**Footer Template:**
```html
<!-- myapp/templates/myapp/includes/footer.html -->
<footer class="your-company-footer">
    <div class="blog-links">
        <a href="{% url 'blog:post_list' %}">Latest Posts</a>
        <a href="{% url 'blog:post_archive' %}">Archive</a>
    </div>
    <!-- Your other footer content -->
</footer>
```

### Benefits

- **Seamless Integration**: Maintain consistent branding across your entire website
- **Flexible Design**: Mix and match default and custom templates
- **Easy Migration**: Switch between designs without changing blog functionality
- **Professional Appearance**: Blog appears as a natural part of your website

### Complete Header/Footer Configuration Options

The header/footer swapping feature supports the following settings:

```python
BLOG_SETTINGS = {
    # Enable/disable custom header
    'USE_CUSTOM_HEADER': False,
    
    # Enable/disable custom footer  
    'USE_CUSTOM_FOOTER': False,
    
    # Default header template (fallback)
    'HEADER_TEMPLATE': 'blog/includes/header.html',
    
    # Default footer template (fallback)
    'FOOTER_TEMPLATE': 'blog/includes/footer.html',
    
    # Path to your custom header template
    'CUSTOM_HEADER_TEMPLATE': None,
    
    # Path to your custom footer template
    'CUSTOM_FOOTER_TEMPLATE': None,
}
```

### Template Requirements

Your custom templates should include blog navigation links:

**Header Template Requirements:**
- Include navigation with blog links
- Use `{% url 'blog:post_list' %}` for blog home
- Use `{% url 'blog:post_archive' %}` for archive
- Use `{% url 'blog:post_search' %}` for search

**Footer Template Requirements:**
- Include blog-related links for easy navigation
- Maintain consistent styling with your website

### Troubleshooting

**Common Issues:**
- Template not found: Verify template paths exist
- Missing blog URLs: Ensure blog app is properly installed
- Styling conflicts: Check CSS loading order and specificity

**Debug Mode:**
Enable Django debug mode to see template loading errors:
```python
DEBUG = True
```

## Usage

### Creating Blog Posts

1. Go to Django admin at `/admin/`
2. Navigate to **Blog → Posts**
3. Create categories and tags as needed
4. Create blog posts with the enhanced CKEditor

### Displaying View Counts

View counts are automatically tracked and available:

```django
{# In templates #}
{{ post.view_count }} views

{# In Python code #}
post.view_count
```

### Template Customization

Override default templates by creating your own:

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

## URL Structure

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

## Troubleshooting

### Common CKEditor Issues

**Error: "No configuration named 'blog_editor' found"**
- **Solution**: Add the `CKEDITOR_CONFIGS` dictionary with `blog_editor` configuration to your `settings.py`

**Error: TemplateDoesNotExist: ckeditor/widget.html**
- **Solution**: Ensure `ckeditor` is in `INSTALLED_APPS` and `APP_DIRS = True` in `TEMPLATES` setting

### Common View Counter Issues

**Views not being counted**
- **Solution**: Verify middleware is in `MIDDLEWARE` list and session middleware is enabled

**Duplicate counts**
- **Solution**: System prevents duplicates within 1 hour - this is normal behavior

### Quick Verification

Run the included configuration checker:
```bash
python check_ckeditor_config.py
```

## Models

### Core Models

- **Category**: Hierarchical organization of posts
- **Tag**: Flexible categorization through many-to-many relationships
- **Post**: Core content with publication workflow
- **Comment**: User engagement with moderation system
- **PostView**: Unique view tracking records

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

# Get view count for a post
post = Post.objects.get(slug='my-post')
views = post.view_count
```

## Admin Interface

The package provides a comprehensive admin interface with:

- Post management with bulk actions
- Category and tag management
- Comment moderation tools
- Publication workflow management
- Search and filtering capabilities
- Enhanced CKEditor for content editing

## Testing

Run the test suite:

```bash
python manage.py test blog
```

## Included Documentation Files

After installation, you'll find these comprehensive documentation files:

- `CKEDITOR_SETUP.md` - Complete CKEditor setup guide
- `CKEDITOR_TROUBLESHOOTING.md` - CKEditor issues and solutions
- `CKEDITOR_SETTINGS_TEMPLATE.py` - Ready-to-copy configuration
- `check_ckeditor_config.py` - Configuration verification script
- `VIEW_COUNTER_SETUP.md` - Complete view counter middleware guide

## Dependencies

- Django >= 4.2, < 5.0
- Pillow >= 9.0, < 11.0
- django-ckeditor >= 6.0, < 7.0

## Compatibility

- Python 3.8+
- Django 4.2+
- SQLite, PostgreSQL, MySQL databases

## Support

For issues and questions:

- Check the included documentation files
- Create an issue on GitHub: https://github.com/josephbraide/django-blog-package/issues
- Review the code examples

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Django Blog Package** - Making blogging in Django projects simple and powerful with professional-grade rich text editing and sophisticated analytics.