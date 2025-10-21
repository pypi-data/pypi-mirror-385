from django.test import TestCase
from django.contrib.auth.models import User
from blog.models import Post, Category, Comment
from blog.forms import CommentForm


class CommentFormTest(TestCase):
    """Test cases for CommentForm"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.category = Category.objects.create(name="Test Category")
        self.post = Post.objects.create(
            title="Test Post",
            author=self.user,
            category=self.category,
            content="Test content",
            status=Post.Status.PUBLISHED,
        )

    def test_comment_form_valid_data(self):
        """Test that form is valid with correct data"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_missing_author_name(self):
        """Test that form is invalid without author name"""
        form_data = {
            "author_name": "",
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("author_name", form.errors)

    def test_comment_form_missing_author_email(self):
        """Test that form is invalid without author email"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("author_email", form.errors)

    def test_comment_form_invalid_email(self):
        """Test that form is invalid with invalid email"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "invalid-email",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("author_email", form.errors)

    def test_comment_form_missing_content(self):
        """Test that form is invalid without content"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "",
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_comment_form_content_too_short(self):
        """Test that form is invalid with content that's too short"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "Too short",
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_comment_form_content_minimum_length(self):
        """Test that form is valid with content of minimum length"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "This comment has exactly twenty characters.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_save_method(self):
        """Test that form save method creates comment correctly"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Save without commit to get the comment instance
        comment = form.save(commit=False)
        comment.post = self.post
        comment.save()

        self.assertEqual(comment.author_name, "Test Author")
        self.assertEqual(comment.author_email, "test@example.com")
        self.assertEqual(
            comment.content, "This is a valid comment with sufficient length."
        )
        self.assertEqual(comment.post, self.post)
        self.assertFalse(comment.is_approved)  # Should default to False

    def test_comment_form_save_with_commit_true(self):
        """Test that form save with commit=True creates comment in database"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # This should fail because post is required but not in form data
        with self.assertRaises(ValueError):
            form.save(commit=True)

    def test_comment_form_clean_content_strips_whitespace(self):
        """Test that content is stripped of leading/trailing whitespace"""
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": "   This comment has whitespace.   ",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["content"], "This comment has whitespace.")

    def test_comment_form_clean_author_name_strips_whitespace(self):
        """Test that author name is stripped of leading/trailing whitespace"""
        form_data = {
            "author_name": "   Test Author   ",
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["author_name"], "Test Author")

    def test_comment_form_field_labels(self):
        """Test that form fields have correct labels"""
        form = CommentForm()
        self.assertEqual(form.fields["author_name"].label, "Your name")
        self.assertEqual(form.fields["author_email"].label, "Your email")
        self.assertEqual(form.fields["content"].label, "Comment")

    def test_comment_form_field_help_texts(self):
        """Test that form fields have correct help texts"""
        form = CommentForm()
        self.assertEqual(
            form.fields["content"].help_text,
            "Your comment must be at least 20 characters long.",
        )

    def test_comment_form_field_widgets(self):
        """Test that form fields use correct widgets"""
        form = CommentForm()

        # Author name should use TextInput
        self.assertEqual(
            form.fields["author_name"].widget.__class__.__name__, "TextInput"
        )

        # Author email should use EmailInput
        self.assertEqual(
            form.fields["author_email"].widget.__class__.__name__, "EmailInput"
        )

        # Content should use Textarea
        self.assertEqual(form.fields["content"].widget.__class__.__name__, "Textarea")

    def test_comment_form_field_required_status(self):
        """Test that form fields have correct required status"""
        form = CommentForm()
        self.assertTrue(form.fields["author_name"].required)
        self.assertTrue(form.fields["author_email"].required)
        self.assertTrue(form.fields["content"].required)

    def test_comment_form_with_parent_comment(self):
        """Test that form can handle parent comment (threaded comments)"""
        parent_comment = Comment.objects.create(
            post=self.post,
            author_name="Parent Author",
            author_email="parent@example.com",
            content="This is a parent comment.",
            is_approved=True,
        )

        form_data = {
            "author_name": "Child Author",
            "author_email": "child@example.com",
            "content": "This is a reply to the parent comment.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Save with parent
        comment = form.save(commit=False)
        comment.post = self.post
        comment.parent = parent_comment
        comment.save()

        self.assertEqual(comment.parent, parent_comment)
        self.assertIn(comment, parent_comment.replies.all())

    def test_comment_form_max_length_validation(self):
        """Test that form validates maximum lengths correctly"""
        # Test very long but valid content
        long_content = "a" * 1000  # 1000 characters should be fine
        form_data = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "content": long_content,
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test very long author name (should be fine within reasonable limits)
        long_name = "a" * 100
        form_data = {
            "author_name": long_name,
            "author_email": "test@example.com",
            "content": "This is a valid comment with sufficient length.",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_html_sanitization(self):
        """Test that form doesn't automatically sanitize HTML (Django handles this)"""
        form_data = {
            "author_name": "Test <script>alert('xss')</script>",
            "author_email": "test@example.com",
            "content": "This is <b>bold</b> text with <script>alert('xss')</script>",
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Form should accept the data as-is; sanitization happens elsewhere
        self.assertEqual(
            form.cleaned_data["author_name"], "Test <script>alert('xss')</script>"
        )
        self.assertEqual(
            form.cleaned_data["content"],
            "This is <b>bold</b> text with <script>alert('xss')</script>",
        )
