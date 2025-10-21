# View Counter Middleware Setup Guide

This guide explains how to set up and configure the view counter middleware for the Django Blog Package.

## Overview

The view counter middleware provides sophisticated tracking of unique post views with the following features:

- **Unique View Tracking**: Counts each user only once per post
- **Duplicate Prevention**: Prevents counting the same user multiple times
- **Automatic Cleanup**: Removes old view records after 30 days
- **Performance Optimized**: Uses caching to minimize database impact

## Installation

### 1. Add Middleware to Settings

Add the view counter middleware to your Django project's `settings.py` file:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    
    # Add these two middleware classes
    'blog.middleware.view_counter.ViewCounterMiddleware',
    'blog.middleware.view_counter.ViewCounterCleanupMiddleware',
    
    # ... other middleware
]
```

### 2. Required Dependencies

The view counter requires Django's session middleware to be enabled. Ensure your middleware includes:

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    
    # Session middleware is REQUIRED for view counter to work
    'django.contrib.sessions.middleware.SessionMiddleware',
    
    # ... other middleware
    'blog.middleware.view_counter.ViewCounterMiddleware',
    'blog.middleware.view_counter.ViewCounterCleanupMiddleware',
    
    # ... other middleware
]
```

## How It Works

### ViewCounterMiddleware

This middleware tracks unique post views:

1. **Automatic Detection**: Automatically detects when users visit post detail pages
2. **Unique Identification**: Uses IP address, session key, and user agent for unique user identification
3. **Duplicate Prevention**: Prevents counting the same user multiple times within 1 hour using cache
4. **View Counting**: Creates `PostView` records and increments `post.view_count`

### ViewCounterCleanupMiddleware

This middleware handles cleanup of old view records:

1. **Scheduled Cleanup**: Runs cleanup once per day (24 hours)
2. **Old Record Removal**: Deletes view records older than 30 days
3. **Performance**: Minimal performance impact with infrequent execution

## Usage

### Displaying View Counts

View counts are automatically available on Post objects and can be displayed in templates:

```django
{# In post detail template #}
<div class="view-count">
    {{ post.view_count }} views
</div>

{# In post list template #}
{% for post in posts %}
    <div class="post-preview">
        <h2>{{ post.title }}</h2>
        <p>{{ post.view_count }} views</p>
    </div>
{% endfor %}
```

### Accessing View Data Programmatically

```python
from blog.models import Post

# Get view count for a specific post
post = Post.objects.get(slug='my-post')
views = post.view_count

# Get all views for a post
post_views = post.post_views.all()

# Get unique view count (same as post.view_count)
unique_views = post.post_views.count()
```

## Configuration Options

### Cache Settings

The view counter uses Django's cache framework. Ensure your cache is properly configured:

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        # Or use Redis, Memcached, etc. for production
    }
}
```

### Customizing Tracking Behavior

You can customize the tracking behavior by modifying the cache timeout:

```python
# The default cache timeout for duplicate prevention is 1 hour (3600 seconds)
# This can be adjusted by modifying the cache.set() call in view_counter.py
```

## Troubleshooting

### View Counter Not Working

If views aren't being counted:

1. **Check Middleware Order**: Ensure the middleware is properly added to `MIDDLEWARE`
2. **Verify Session Support**: Django sessions must be enabled
3. **Check URLs**: The view counter only works with the built-in `PostDetailView` URLs
4. **Enable Debug Mode**: Check Django logs for any middleware errors

### Common Issues

#### Issue: Views not being counted
**Solution**: 
- Verify middleware is in `MIDDLEWARE` list
- Check that you're using the built-in `PostDetailView`
- Ensure sessions are working (check for session cookies)

#### Issue: Duplicate counts for same user
**Solution**: 
- This is normal if cache is cleared or expired
- The system prevents duplicates within 1 hour by default

#### Issue: Performance impact
**Solution**:
- Ensure cache is properly configured
- The cleanup middleware runs only once per day
- View tracking uses cache to minimize database hits

### Debug Mode

Enable debug mode to see detailed information:

```python
# settings.py
DEBUG = True

# Add logging to see view counter activity
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'blog.middleware.view_counter': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

## Database Schema

The view counter uses the following models:

### PostView Model
- `post`: ForeignKey to Post
- `ip_address`: Client IP address
- `user_agent`: Browser user agent (truncated)
- `session_key`: Django session key
- `user`: Authenticated user (optional)
- `created_at`: Timestamp of view

### Post Model
- `view_count`: Integer field tracking total unique views

## Performance Considerations

- **Cache Usage**: Heavy reliance on cache for performance
- **Database Optimization**: Cleanup runs infrequently
- **Session Dependency**: Requires session middleware
- **IP-Based Tracking**: May be less accurate behind proxies/NAT

## Security and Privacy

- **IP Address Storage**: Client IP addresses are stored
- **User Agent Storage**: Browser information is stored (truncated)
- **Session Tracking**: Uses Django session framework
- **Data Retention**: View records are automatically deleted after 30 days

## Customization

### Extending Functionality

You can extend the view counter by creating custom middleware:

```python
# custom_middleware.py
from blog.middleware.view_counter import ViewCounterMiddleware

class CustomViewCounterMiddleware(ViewCounterMiddleware):
    def track_view(self, request, year, month, day, slug):
        # Add custom logic before tracking
        print(f"Tracking view for {slug}")
        
        # Call parent method
        super().track_view(request, year, month, day, slug)
        
        # Add custom logic after tracking
        print(f"View tracked for {slug}")
```

## Support

If you encounter issues with the view counter:

1. **Check this guide** for common solutions
2. **Verify middleware configuration** in your settings
3. **Check Django logs** for error messages
4. **Ensure session middleware** is properly configured

Remember: The view counter middleware must be added to your project's `MIDDLEWARE` setting to function properly.