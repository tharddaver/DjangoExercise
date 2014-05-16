from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory
from rango import views
from rango.forms import UserForm, UserRegistrationForm
from rango.models import Category, Page, User


class IndexTest(TestCase):
    def test_index(self):
        url = reverse('rango.views.index')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_about(self):
        url = reverse('rango.views.about')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)


class CategoryTest(TestCase):
    def test_index_category_list(self):
        category = Category.objects.create(name='Test Category')

        url = reverse('rango.views.index')
        response = self.client.get(url)

        self.assertContains(response, category.name, 2, 200)

    def test_category_page(self):
        category = Category.objects.create(name='Test Category')

        url = reverse('rango.views.category',
                      kwargs={'category_slug': category.slug})
        response = self.client.get(url)

        self.assertContains(response, category.name, status_code=200)

    def test_add_category_unauthorized(self):
        url = reverse('rango.views.add_category')
        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse('rango.views.user_login') + '?next=' + url
        )

    def test_add_category_authorized(self):
        url = reverse('rango.views.add_category')

        request = RequestFactory().get(url)
        request.user = self.__create_user()
        response = views.add_category(request)
        self.assertEqual(response.status_code, 200)

    def test_add_category_valid(self):
        url = reverse('rango.views.add_category')

        request = RequestFactory().post(url, {'name': 'Test Category Name'})
        request.user = self.__create_user()
        response = views.add_category(request)
        self.assertEqual(response.status_code, 302)

    def test_suggest_category(self):
        category = Category.objects.create(name='Suggestion Test Category')
        url = reverse('rango.views.suggest_category')
        response = self.client.get(url, {'suggestion': 'Sugg'})

        self.assertContains(response, category.name, 1, 200)

    def test_like_category(self):
        category = Category.objects.create(name='Test Category')
        request = RequestFactory().get(
            reverse('rango.views.like_category')
            + '?category_id=' + str(category.id)
        )
        request.user = self.__create_user()

        response = views.like_category(request)
        self.assertEqual(int(response.content), 1)

    def __create_user(self):
        return User.objects.create_user(username='test_user', password='123')


class PageTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.user = User.objects.create_user(username='test_user',
                                             password='123')

    def test_add_page_unauthorized(self):
        url = reverse('rango.views.add_page',
                      kwargs={'category_slug': self.category.slug})
        response = self.client.get(url)

        self.assertRedirects(
            response,
            reverse('rango.views.user_login') + '?next=' + url
        )

    def test_add_page_authorized(self):
        url = reverse('rango.views.add_page',
                      kwargs={'category_slug': self.category.slug})

        request = RequestFactory().get(url)
        request.user = self.user
        response = views.add_page(request, self.category.slug)
        self.assertEqual(response.status_code, 200)

    def test_add_page_valid(self):
        url = reverse('rango.views.add_page',
                      kwargs={'category_slug': self.category.slug})

        request = RequestFactory().post(url, {'title': 'Test Page',
                                              'url': 'http://url.com'})
        request.user = self.user
        response = views.add_page(request, self.category.slug)
        self.assertEqual(response.status_code, 302)

    def test_add_page_ajax(self):
        url = reverse('rango.views.add_page',
                      kwargs={'category_slug': self.category.slug})
        request = RequestFactory().post(
            url,
            {'title': 'Test Page', 'url': 'http://url.com'}
        )
        request.user = self.user
        request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
        response = views.add_page(request, self.category.slug)
        self.assertEqual(response.status_code, 200)

    def test_track_url(self):
        page = Page.objects.create(
            category=Category.objects.create(name='Category'),
            title='Page', url='http://url.com'
        )

        response = self.client.get(
            reverse('rango.views.track_url') + '?page_id=' + str(page.id)
        )
        self.assertEqual(response._headers['location'], ('Location', page.url))


class UserTest(TestCase):
    def test_registration(self):
        url = reverse('rango.views.register')

        response = self.client.post(url, {'username': 'username',
                                          'password': 12345})
        self.assertEqual(response.status_code, 200)

    def test_edit_profile(self):
        request = RequestFactory().post(
            reverse('rango.views.profile_edit'),
            {'username': 'test_username'}
        )
        request.user = User.objects.create(username='username',
                                           password='12345')
        response = views.profile_edit(request)

        self.assertEqual(response.status_code, 200)

    def test_user_login_incorrect(self):
        response = self.client.post(
            reverse('rango.views.user_login'),
            {'username': 'username', 'password': '12345'}
        )
        self.assertTrue(response.status_code, 200)

    def test_user_login(self):
        user = UserRegistrationForm(
            data={'username': 'username', 'password': '12345'}).save()
        response = self.client.post(
            reverse('rango.views.user_login'),
            {'username': 'username', 'password': '12345'}
        )
        self.assertRedirects(response, reverse('rango.views.index'))
        self.assertEqual(self.client.session['_auth_user_id'], user.pk)