#!/usr/bin/env python
"""
CKEditor Configuration Checker for Django Blog Package

This script helps users verify that their CKEditor configuration is properly set up
for the Django Blog Package. Run this script from your Django project directory.

Usage:
    python check_ckeditor_config.py
"""

import os
import sys
import django


def setup_django():
    """Setup Django environment."""
    try:
        # Try to import Django settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
        sys.path.insert(0, os.path.dirname(os.path.abspath(".")))

        # Import Django
        import django
        from django.conf import settings

        # Configure Django
        django.setup()
        return settings
    except ImportError:
        print("❌ Django not found. Make sure you're in a Django project directory.")
        return None
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        print("   Make sure you're in your Django project directory and")
        print("   update 'your_project_name.settings' with your actual project name.")
        return None


def check_ckeditor_config(settings):
    """Check CKEditor configuration."""
    print("🔍 Checking CKEditor Configuration for Django Blog Package")
    print("=" * 60)

    all_checks_passed = True

    # 1. Check INSTALLED_APPS
    print("\n1. Checking INSTALLED_APPS...")
    if "ckeditor" in settings.INSTALLED_APPS:
        print("   ✅ CKEditor is in INSTALLED_APPS")
    else:
        print("   ❌ CKEditor is NOT in INSTALLED_APPS")
        print("   → Add 'ckeditor' to your INSTALLED_APPS in settings.py")
        all_checks_passed = False

    # Check if blog is after ckeditor
    try:
        ckeditor_index = settings.INSTALLED_APPS.index("ckeditor")
        blog_index = settings.INSTALLED_APPS.index("blog")
        if blog_index > ckeditor_index:
            print("   ✅ Blog app is correctly placed after CKEditor")
        else:
            print("   ⚠️  Blog app should be placed AFTER CKEditor in INSTALLED_APPS")
    except ValueError:
        pass  # One of the apps is not installed

    # 2. Check CKEDITOR_CONFIGS
    print("\n2. Checking CKEDITOR_CONFIGS...")
    if hasattr(settings, "CKEDITOR_CONFIGS"):
        print("   ✅ CKEDITOR_CONFIGS is defined")

        if "blog_editor" in settings.CKEDITOR_CONFIGS:
            print("   ✅ 'blog_editor' configuration found")
            config = settings.CKEDITOR_CONFIGS["blog_editor"]

            # Check key features
            if config.get("toolbar") == "Full":
                print("   ✅ Full toolbar enabled")
            else:
                print(f"   ⚠️  Toolbar: {config.get('toolbar')} (Full recommended)")

            # Check for search functionality
            extra_plugins = config.get("extraPlugins", "")
            if "find" in extra_plugins:
                print("   ✅ Find/Replace plugin enabled (Ctrl+F)")
            else:
                print("   ❌ Find/Replace plugin not found")
                all_checks_passed = False

            # Check height
            if config.get("height") == 500:
                print("   ✅ Enhanced height (500px) configured")
            else:
                print(f"   ⚠️  Height: {config.get('height')}px (500px recommended)")

        else:
            print("   ❌ 'blog_editor' configuration not found")
            print("   → Add the 'blog_editor' configuration to CKEDITOR_CONFIGS")
            all_checks_passed = False
    else:
        print("   ❌ CKEDITOR_CONFIGS not defined")
        print("   → Add CKEDITOR_CONFIGS to your settings.py")
        all_checks_passed = False

    # 3. Check Media Settings
    print("\n3. Checking Media Settings...")
    if hasattr(settings, "MEDIA_URL") and settings.MEDIA_URL:
        print(f"   ✅ MEDIA_URL: {settings.MEDIA_URL}")
    else:
        print("   ❌ MEDIA_URL not configured")
        print("   → Add MEDIA_URL = '/media/' to your settings.py")
        all_checks_passed = False

    if hasattr(settings, "MEDIA_ROOT") and settings.MEDIA_ROOT:
        print(f"   ✅ MEDIA_ROOT: {settings.MEDIA_ROOT}")
    else:
        print("   ❌ MEDIA_ROOT not configured")
        print(
            "   → Add MEDIA_ROOT = os.path.join(BASE_DIR, 'media/') to your settings.py"
        )
        all_checks_passed = False

    # 4. Check URL Configuration
    print("\n4. Checking URL Configuration...")
    print("   ℹ️  Manual check required:")
    print(
        "   → Ensure your urls.py includes: path('ckeditor/', include('ckeditor_uploader.urls'))"
    )

    # 5. Test Template Loading
    print("\n5. Testing Template Loading...")
    try:
        from django.template.loader import get_template

        template = get_template("ckeditor/widget.html")
        print("   ✅ CKEditor widget template loads successfully")
    except Exception as e:
        print(f"   ❌ Template loading error: {e}")
        print("   → Run: python manage.py collectstatic")
        all_checks_passed = False

    return all_checks_passed


def display_results(all_checks_passed):
    """Display final results and next steps."""
    print("\n" + "=" * 60)

    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("=" * 60)
        print("\n✅ Your CKEditor configuration is ready!")
        print("\nNext steps:")
        print("1. Run: python manage.py collectstatic")
        print("2. Run: python manage.py migrate")
        print("3. Start your server: python manage.py runserver")
        print("4. Visit /admin/blog/post/ to test CKEditor")
        print("\nTo use search & replace:")
        print("  • Press Ctrl+F in the editor")
        print("  • Use the Replace tab to find and replace text")
    else:
        print("❌ CONFIGURATION ISSUES FOUND")
        print("=" * 60)
        print("\nPlease fix the issues above and run this script again.")
        print("\nQuick setup template:")
        print("1. Copy configuration from CKEDITOR_SETUP.md")
        print("2. Add to your project's settings.py")
        print("3. Add CKEditor URLs to urls.py")
        print("4. Run collectstatic and migrate commands")


def main():
    """Main function."""
    settings = setup_django()
    if not settings:
        return 1

    try:
        all_checks_passed = check_ckeditor_config(settings)
        display_results(all_checks_passed)
        return 0 if all_checks_passed else 1
    except Exception as e:
        print(f"\n❌ Error during configuration check: {e}")
        print("\nMake sure:")
        print("1. You're in your Django project directory")
        print("2. Your virtual environment is activated")
        print("3. Django is properly installed")
        return 1


if __name__ == "__main__":
    # Update the settings module with user's project name
    if len(sys.argv) > 1:
        os.environ["DJANGO_SETTINGS_MODULE"] = f"{sys.argv[1]}.settings"
    else:
        print("ℹ️  Usage: python check_ckeditor_config.py [your_project_name]")
        print("   If not specified, will try 'your_project_name.settings'")
        print()

    sys.exit(main())
