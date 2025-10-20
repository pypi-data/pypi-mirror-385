from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-blog-package",
    version="1.0.6",
    author="Joseph Braide",
    author_email="braidejgmail.com",
    description="A reusable Django blog package for adding blog functionality to any Django project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/josephbraide/django-blog-package",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.2,<5.0",
        "Pillow>=9.0,<11.0",
        "django-ckeditor>=6.0,<7.0",
    ],
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "django",
        "blog",
        "cms",
        "content",
        "posts",
        "articles",
        "comments",
        "categories",
        "tags",
    ],
    project_urls={
        "Bug Reports": "https://github.com/josephbraide/django-blog-package/issues",
        "Source": "https://github.com/josephbraide/django-blog-package",
        "Documentation": "https://github.com/josephbraide/django-blog-package/blob/main/README.md",
    },
)
