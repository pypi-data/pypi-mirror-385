# Django CKEditor Setup Guide

> **Important**: This guide explains how to properly configure CKEditor when using the Django Blog Package in your project.

## Installation

### 1. Install Dependencies

The blog package automatically includes `django-ckeditor` as a dependency, so it will be installed when you install the blog package:

```bash
pip install django-blog-package
```

### 2. Add to INSTALLED_APPS

Add CKEditor to your Django project's `settings.py` **before** the blog app:

```python
# settings.py
INSTALLED_APPS = [
    # ... other Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    
    # Add CKEditor BEFORE the blog app
    'ckeditor',
    'ckeditor_uploader',  # Optional, for file uploads
    
    # Then add the blog package
    'blog',
]
```

## Required Configuration

### 1. Add CKEditor Configuration to Your Settings

**You MUST add this configuration to your project's `settings.py` file:**

```python
# settings.py

# Media configuration (required for file uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# CKEditor basic settings
CKEDITOR_UPLOAD_PATH = "blog/uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

# CKEditor configuration for blog posts
# THIS IS REQUIRED - the blog package expects this configuration
CKEDITOR_CONFIGS = {
    'blog_editor': {
        'toolbar': 'Full',
        'toolbar_Full': [
            ['Source', '-', 'Save', 'NewPage', 'Preview', '-', 'Templates'],
            ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Print', 'SpellChecker', 'Scayt'],
            ['Undo', 'Redo', '-', 'Find', 'Replace', '-', 'SelectAll', 'RemoveFormat'],
            ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
            '/',
            ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'CopyFormatting', 'RemoveFormat'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe'],
            '/',
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
            ['Maximize', 'ShowBlocks'],
            ['About']
        ],
        'height': 500,
        'width': '100%',
        'extraPlugins': 'codesnippet,image2,uploadimage,find,autolink,autoembed,embedsemantic,autogrow',
        'removePlugins': 'elementspath',
        'resize_enabled': True,
        'allowedContent': True,
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserUploadMethod': 'form',
        'contentsCss': [
            'https://cdn.tailwindcss.com',
            '/static/blog/css/custom.css',
        ],
        'stylesSet': 'blog_styles',
        'format_tags': 'p;h1;h2;h3;h4;h5;h6;pre;address;div',
        'removeDialogTabs': 'image:advanced;link:advanced',
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

### 2. URL Configuration

Add CKEditor URLs to your project's `urls.py`:

```python
# urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... your other URL patterns
    
    # Add CKEditor URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Enhanced Features Available

The blog package comes with a fully configured CKEditor that includes:

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

## Usage

### In Django Admin

Once configured, CKEditor will automatically appear in the Django admin when creating or editing blog posts:

1. Go to `/admin/`
2. Navigate to **Blog → Posts**
3. Create or edit a post
4. The enhanced CKEditor will be available for the content field

### Using Search & Replace

To find and replace repeated characters:

1. **Press Ctrl+F** to open the Find dialog
2. **Enter the text** you want to search for
3. **Switch to the Replace tab**
4. **Enter replacement text**
5. Click **Replace** (single instance) or **Replace All** (all instances)

## Troubleshooting

### Common Errors

#### Error: "No configuration named 'blog_editor' found"

**Problem**: The CKEditor configuration is missing from your project's settings.

**Solution**: Add the `CKEDITOR_CONFIGS` dictionary with the `blog_editor` configuration to your `settings.py` file as shown above.

#### Error: TemplateDoesNotExist: ckeditor/widget.html

**Problem**: CKEditor is not properly installed or configured.

**Solutions**:
1. Ensure `ckeditor` is in `INSTALLED_APPS`
2. Make sure `APP_DIRS = True` in your `TEMPLATES` setting
3. Run `python manage.py collectstatic`

#### Error: CKEditor not loading in admin

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify static files are served correctly
3. Ensure CKEditor URLs are included in your `urls.py`

### Quick Setup Checklist

- [ ] `ckeditor` added to `INSTALLED_APPS` (before `blog`)
- [ ] `CKEDITOR_CONFIGS` with `blog_editor` configuration added to `settings.py`
- [ ] `MEDIA_URL` and `MEDIA_ROOT` configured
- [ ] CKEditor URLs added to `urls.py`
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Migrations run (`python manage.py migrate`)

## Customization

### Adding Custom CSS

Create a custom CSS file to style CKEditor content:

```css
/* static/blog/css/custom.css */
.ck-content {
    font-family: 'Inter', system-ui, sans-serif;
    line-height: 1.6;
    color: #374151;
}

.ck-content h1, .ck-content h2, .ck-content h3 {
    font-weight: 700;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

.ck-content h1 { font-size: 2.25rem; }
.ck-content h2 { font-size: 1.875rem; }
.ck-content h3 { font-size: 1.5rem; }

.ck-content p {
    margin-bottom: 1em;
}

.ck-content blockquote {
    border-left: 4px solid #3b82f6;
    padding-left: 1em;
    margin-left: 0;
    font-style: italic;
    color: #6b7280;
}
```

### Modifying the Configuration

You can customize the CKEditor configuration by modifying the `blog_editor` configuration in your `settings.py`:

```python
# To add more plugins
'extraPlugins': 'codesnippet,image2,uploadimage,find,autolink,your_custom_plugin',

# To change the toolbar
'toolbar': 'Custom',
'toolbar_Custom': [
    # Your custom toolbar configuration
],
```

## Security Considerations

### File Upload Security

- Configure file upload restrictions in production
- Validate file types and sizes
- Use secure file storage
- Consider using cloud storage for production

### Content Security Policy

If using CSP, ensure CKEditor is allowed:

```python
# settings.py
CSP_STYLE_SRC = ["'self'", "https://cdn.tailwindcss.com"]
CSP_SCRIPT_SRC = ["'self'", "'unsafe-inline'"]  # CKEditor requires unsafe-inline
```

## Support

If you encounter issues:

1. **Check this guide** first for common solutions
2. **Verify your configuration** matches the examples above
3. **Check the Django CKEditor documentation**: https://django-ckeditor.readthedocs.io/

---

**Remember**: The CKEditor configuration must be added to your **project's** `settings.py` file, not just the package's settings. This is the most common cause of configuration errors.