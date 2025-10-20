from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import BlogPost, Category, Tag
from accounts.models import AdminProfile

User = get_user_model()


class BlogApprovalWorkflowTestCase(TestCase):
    """Test the complete blog approval workflow"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.site_manager = User.objects.create_user(
            username='sitemanager',
            email='sitemanager@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.public_user = User.objects.create_user(
            username='public',
            email='public@test.com',
            password='testpass123'
        )
        
        # Create admin profiles
        self.site_manager_profile = AdminProfile.objects.create(
            user=self.site_manager,
            admin_role='site_manager',
            approval_status='approved'
        )
        
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            admin_role='admin',
            approval_status='approved'
        )
        
        # Create category
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create test blog posts
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='This is a draft post',
            author=self.site_manager,
            category=self.category,
            status='draft'
        )
        
        self.published_post = BlogPost.objects.create(
            title='Published Post',
            slug='published-post',
            content='This is a published post',
            author=self.site_manager,
            category=self.category,
            status='published'
        )
        
        self.archived_post = BlogPost.objects.create(
            title='Archived Post',
            slug='archived-post',
            content='This is an archived post',
            author=self.site_manager,
            category=self.category,
            status='archived'
        )
        
        self.client = Client()
    
    def test_site_manager_can_create_blog(self):
        """Test that site manager can create a blog post"""
        self.client.login(username='sitemanager', password='testpass123')
        
        response = self.client.post(reverse('blog:create_blog_post'), {
            'title': 'New Blog Post',
            'content': 'Content of new blog post',
            'category': self.category.id,
            'status': 'published'
        })
        
        # Should redirect to drafts page
        self.assertEqual(response.status_code, 302)
        
        # Blog post should be created
        self.assertTrue(BlogPost.objects.filter(title='New Blog Post').exists())
    
    def test_admin_sees_only_published_and_archived(self):
        """Test that admin management only shows published and archived posts"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('blog:blogmanagement'))
        self.assertEqual(response.status_code, 200)
        
        # Should see published and archived posts
        self.assertIn(self.published_post, response.context['blog_posts'])
        self.assertIn(self.archived_post, response.context['blog_posts'])
        
        # Should NOT see draft posts
        self.assertNotIn(self.draft_post, response.context['blog_posts'])
    
    def test_site_manager_sees_own_posts_in_drafts(self):
        """Test that site manager sees all their posts in drafts page"""
        self.client.login(username='sitemanager', password='testpass123')
        
        response = self.client.get(reverse('blog:blog_drafts'))
        self.assertEqual(response.status_code, 200)
        
        # Should see all their posts
        self.assertIn(self.draft_post, response.context['blog_posts'])
        self.assertIn(self.published_post, response.context['blog_posts'])
        self.assertIn(self.archived_post, response.context['blog_posts'])
    
    def test_admin_can_approve_blog(self):
        """Test that admin can approve a published blog post"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post(
            reverse('blog:approve_blog_post', kwargs={'post_id': self.published_post.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Refresh from database
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.status, 'published')
    
    def test_admin_can_reject_blog(self):
        """Test that admin can reject a blog post (send back to draft)"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post(
            reverse('blog:reject_blog_post', kwargs={'post_id': self.published_post.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Refresh from database
        self.published_post.refresh_from_db()
        self.assertEqual(self.published_post.status, 'draft')
    
    def test_public_sees_only_published_posts(self):
        """Test that public blog list only shows published posts"""
        response = self.client.get(reverse('blog:blog_list'))
        self.assertEqual(response.status_code, 200)
        
        # Get the posts from the paginated object
        posts = response.context['page_obj'].object_list
        
        # Should see published post
        self.assertIn(self.published_post, posts)
        
        # Should NOT see draft or archived posts
        self.assertNotIn(self.draft_post, posts)
        self.assertNotIn(self.archived_post, posts)
    
    def test_public_can_view_published_post_detail(self):
        """Test that public can view published post detail"""
        response = self.client.get(
            reverse('blog:blog_detail', kwargs={'slug': self.published_post.slug})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['blog_post'], self.published_post)
    
    def test_public_cannot_view_draft_post_detail(self):
        """Test that public cannot view draft post detail"""
        response = self.client.get(
            reverse('blog:blog_detail', kwargs={'slug': self.draft_post.slug})
        )
        
        # Should return 404
        self.assertEqual(response.status_code, 404)
    
    def test_non_admin_cannot_approve_blog(self):
        """Test that non-admin users cannot approve blogs"""
        self.client.login(username='public', password='testpass123')
        
        response = self.client.post(
            reverse('blog:approve_blog_post', kwargs={'post_id': self.published_post.id})
        )
        
        # Should redirect (no access)
        self.assertEqual(response.status_code, 302)
    
    def test_non_admin_cannot_access_blog_management(self):
        """Test that non-admin users cannot access blog management"""
        self.client.login(username='public', password='testpass123')
        
        response = self.client.get(reverse('blog:blogmanagement'))
        
        # Should redirect (no access)
        self.assertEqual(response.status_code, 302)
    
    def test_blog_creation_redirects_to_drafts(self):
        """Test that blog creation redirects to drafts page"""
        self.client.login(username='sitemanager', password='testpass123')
        
        response = self.client.post(reverse('blog:create_blog_post'), {
            'title': 'Test Redirect Post',
            'content': 'Content',
            'category': self.category.id,
            'status': 'draft'
        })
        
        # Should redirect to drafts page
        self.assertRedirects(response, reverse('blog:blog_drafts'))


class BlogStatusFilterTestCase(TestCase):
    """Test blog status filtering in different views"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_superuser=True,
            is_staff=True
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        
        # Create posts with different statuses
        self.statuses = ['draft', 'published', 'archived']
        self.posts = {}
        
        for status in self.statuses:
            self.posts[status] = BlogPost.objects.create(
                title=f'{status.title()} Post',
                slug=f'{status}-post',
                content=f'This is a {status} post',
                author=self.admin_user,
                category=self.category,
                status=status
            )
        
        self.client = Client()
    
    def test_draft_post_count_in_admin_management(self):
        """Test that admin management shows correct draft count"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('blog:blogmanagement'))
        self.assertEqual(response.status_code, 200)
        
        # Should show draft count in stats
        self.assertEqual(response.context['draft_posts'], 1)
    
    def test_published_posts_visible_in_admin_management(self):
        """Test that published posts are visible in admin management"""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.get(reverse('blog:blogmanagement'))
        
        blog_posts = list(response.context['blog_posts'])
        self.assertIn(self.posts['published'], blog_posts)
        self.assertNotIn(self.posts['draft'], blog_posts)
