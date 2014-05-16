from django.test import TestCase
from rango.models import Category, Page, User


class CategoryTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name='Test Category', views=16,
                                           likes=20)
        self.assertIsInstance(category, Category)
        self.assertEqual(category.__unicode__(), 'Test Category')
        self.assertEqual(category.slug, 'test-category')


class PageTest(TestCase):
    def test_page_creation(self):
        category = Category.objects.create(name='Test Category')
        page = Page.objects.create(category=category, title='Test Page',
                                   url='http://test-page.com', views=20)
        self.assertIsInstance(page, Page)
        self.assertEqual(page.__unicode__(), 'Test Page')


class UserProfileTest(TestCase):
    def test_user_profile_auto_creation(self):
        user = User.objects.create_user(username='admin')
        self.assertIsInstance(user, User)
        self.assertEqual(user.__unicode__(), 'admin')