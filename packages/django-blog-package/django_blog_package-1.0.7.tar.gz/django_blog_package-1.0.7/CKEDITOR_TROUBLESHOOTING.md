# CKEditor Troubleshooting Guide

This guide helps you resolve common issues when setting up CKEditor with the Django Blog Package.

## Common Errors and Solutions

### Error: "No configuration named 'blog_editor' found"

**Problem**: The CKEditor configuration is missing from your project's settings.

**Solution**: Add the following to your `settings.py` file:

```python
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

### Error: "TemplateDoesNotExist: ckeditor/widget.html"

**Problem**: CKEditor templates cannot be found.

**Solutions**:

1. **Check INSTALLED_APPS**:
   ```python
   # settings.py
   INSTALLED_APPS = [
       # ... other apps
       'ckeditor',  # Make sure this is included
       'blog',
   ]
   ```

2. **Check TEMPLATES setting**:
   ```python
   # settings.py
   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [],
           'APP_DIRS': True,  # This MUST be True
           # ...
       },
   ]
   ```

3. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Restart development server** after making changes.

### Error: CKEditor not loading in admin

**Problem**: The editor appears as a plain textarea instead of a rich text editor.

**Solutions**:

1. **Check browser console** for JavaScript errors
2. **Verify static files** are being served:
   - Check that `DEBUG = True` in development
   - Run `python manage.py collectstatic`
   - Ensure static files URL is configured

3. **Check URL configuration**:
   ```python
   # urls.py
   from django.urls import path, include

   urlpatterns = [
       # ... other URLs
       path('ckeditor/', include('ckeditor_uploader.urls')),
   ]
   ```

### Error: File upload not working

**Problem**: Cannot upload images or files through CKEditor.

**Solutions**:

1. **Check media configuration**:
   ```python
   # settings.py
   MEDIA_URL = '/media/'
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
   ```

2. **Check URL configuration for media files**:
   ```python
   # urls.py (development only)
   from django.conf import settings
   from django.conf.urls.static import static

   if settings.DEBUG:
       urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
   ```

3. **Check file permissions** for the media directory

### Error: Search and Replace not working

**Problem**: Ctrl+F doesn't open find dialog or replace functionality is missing.

**Solutions**:

1. **Verify 'find' plugin** is included:
   ```python
   # settings.py
   CKEDITOR_CONFIGS = {
       'blog_editor': {
           'extraPlugins': 'find,autogrow,...',  # Make sure 'find' is included
           # ...
       }
   }
   ```

2. **Check browser compatibility** - some features may not work in older browsers
3. **Try different keyboard shortcuts**:
   - Ctrl+F (Windows/Linux)
   - Cmd+F (Mac)

## Quick Setup Checklist

Use this checklist to ensure everything is properly configured:

- [ ] `ckeditor` added to `INSTALLED_APPS` (before `blog`)
- [ ] `CKEDITOR_CONFIGS` with `blog_editor` configuration added to `settings.py`
- [ ] `MEDIA_URL` and `MEDIA_ROOT` configured in `settings.py`
- [ ] CKEditor URLs added to `urls.py`
- [ ] Media URLs configured in `urls.py` (for development)
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Migrations run: `python manage.py migrate`
- [ ] Development server restarted after configuration changes

## Debugging Steps

### 1. Enable Debug Mode

```python
# settings.py
DEBUG = True
```

### 2. Check Django Logs

Look for error messages in your terminal where the development server is running.

### 3. Browser Developer Tools

1. Open browser developer tools (F12)
2. Check the Console tab for JavaScript errors
3. Check the Network tab for failed resource loads

### 4. Verify Configuration

Run the configuration checker:
```bash
python check_ckeditor_config.py
```

## Common Configuration Mistakes

### Mistake 1: Missing CKEditor in INSTALLED_APPS

**Wrong**:
```python
INSTALLED_APPS = [
    'blog',
    # ckeditor missing
]
```

**Correct**:
```python
INSTALLED_APPS = [
    'ckeditor',
    'blog',
]
```

### Mistake 2: Wrong CKEDITOR_CONFIGS name

**Wrong**:
```python
CKEDITOR_CONFIGS = {
    'default': {  # Should be 'blog_editor'
        # ...
    }
}
```

**Correct**:
```python
CKEDITOR_CONFIGS = {
    'blog_editor': {
        # ...
    }
}
```

### Mistake 3: Missing Media Configuration

**Wrong**:
```python
# MEDIA_URL and MEDIA_ROOT missing
```

**Correct**:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
```

## Testing Your Setup

After fixing configuration issues:

1. **Restart your development server**
2. **Visit the admin**: `/admin/blog/post/add/`
3. **Test CKEditor features**:
   - Type some text
   - Try formatting (bold, italic)
   - Press Ctrl+F to test search
   - Try uploading an image (if configured)

## Getting Help

If you're still having issues:

1. **Check the documentation**: [CKEDITOR_SETUP.md](CKEDITOR_SETUP.md)
2. **Verify your Django version**: `python -m django --version`
3. **Check CKEditor version**: `pip show django-ckeditor`
4. **Look for similar issues** in the package repository

Remember: The CKEditor configuration must be in your **project's** `settings.py`, not just the package's test settings.