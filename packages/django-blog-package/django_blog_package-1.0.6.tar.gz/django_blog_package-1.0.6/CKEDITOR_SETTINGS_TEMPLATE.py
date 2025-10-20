# CKEditor Settings Template for Django Blog Package
# Copy and paste this configuration into your Django project's settings.py file

# Media configuration (required for file uploads)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media/")

# CKEditor basic settings
CKEDITOR_UPLOAD_PATH = "blog/uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_ALLOW_NONIMAGE_FILES = False

# CKEditor configuration for blog posts
# THIS IS REQUIRED - the blog package expects this configuration
CKEDITOR_CONFIGS = {
    "blog_editor": {
        "toolbar": "Full",
        "toolbar_Full": [
            ["Source", "-", "Save", "NewPage", "Preview", "-", "Templates"],
            [
                "Cut",
                "Copy",
                "Paste",
                "PasteText",
                "PasteFromWord",
                "-",
                "Print",
                "SpellChecker",
                "Scayt",
            ],
            ["Undo", "Redo", "-", "Find", "Replace", "-", "SelectAll", "RemoveFormat"],
            [
                "Form",
                "Checkbox",
                "Radio",
                "TextField",
                "Textarea",
                "Select",
                "Button",
                "ImageButton",
                "HiddenField",
            ],
            "/",
            [
                "Bold",
                "Italic",
                "Underline",
                "Strike",
                "Subscript",
                "Superscript",
                "-",
                "CopyFormatting",
                "RemoveFormat",
            ],
            [
                "NumberedList",
                "BulletedList",
                "-",
                "Outdent",
                "Indent",
                "-",
                "Blockquote",
                "CreateDiv",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
                "-",
                "BidiLtr",
                "BidiRtl",
            ],
            ["Link", "Unlink", "Anchor"],
            [
                "Image",
                "Flash",
                "Table",
                "HorizontalRule",
                "Smiley",
                "SpecialChar",
                "PageBreak",
                "Iframe",
            ],
            "/",
            ["Styles", "Format", "Font", "FontSize"],
            ["TextColor", "BGColor"],
            ["Maximize", "ShowBlocks"],
            ["About"],
        ],
        "height": 500,
        "width": "100%",
        "extraPlugins": "codesnippet,image2,uploadimage,find,autolink,autoembed,embedsemantic,autogrow",
        "removePlugins": "elementspath",
        "resize_enabled": True,
        "allowedContent": True,
        "filebrowserUploadUrl": "/ckeditor/upload/",
        "filebrowserUploadMethod": "form",
        "contentsCss": [
            "https://cdn.tailwindcss.com",
            "/static/blog/css/custom.css",
        ],
        "stylesSet": "blog_styles",
        "format_tags": "p;h1;h2;h3;h4;h5;h6;pre;address;div",
        "removeDialogTabs": "image:advanced;link:advanced",
        "autoGrow_minHeight": 400,
        "autoGrow_maxHeight": 1200,
        "autoGrow_bottomSpace": 50,
        "autoGrow_onStartup": True,
        "wordcount": {
            "showParagraphs": True,
            "showWordCount": True,
            "showCharCount": True,
            "countSpacesAsChars": True,
            "countHTML": False,
        },
        "linkDefaultTarget": "_blank",
        "find_highlight": {
            "element": "span",
            "styles": {"background-color": "#ffeb3b", "color": "#000000"},
        },
        "scayt_autoStartup": True,
        "scayt_sLang": "en_US",
        "scayt_maxSuggestions": 5,
        "scayt_minWordLength": 4,
    }
}

# URL Configuration (add to your urls.py)
"""
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
"""

# INSTALLED_APPS Configuration (add to your settings.py)
"""
INSTALLED_APPS = [
    # ... other Django apps

    # Add CKEditor BEFORE the blog app
    'ckeditor',
    'ckeditor_uploader',  # Optional, for file uploads

    # Then add the blog package
    'blog',
]
"""
