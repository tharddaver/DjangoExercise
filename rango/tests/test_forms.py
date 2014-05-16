from django.test import TestCase
from rango.forms import CategoryForm, PageForm, UserForm


class CategoryFormTest(TestCase):
    def test_valid_form(self):
        data = {'name': 'Test Category'}
        form = CategoryForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'name': ''}
        form = CategoryForm(data=data)
        self.assertFalse(form.is_valid())


class PageFormTest(TestCase):
    def test_valid_form(self):
        data = {'title': 'Test Category', 'url': 'test-url.com'}
        form = PageForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'title': '', 'url': ''}
        form = PageForm(data=data)
        self.assertFalse(form.is_valid())


class UserFormTest(TestCase):
    def test_valid_form(self):
        data = {'username': 'test_username'}
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {'username': ''}
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())
        data['email'] = 'wrongemail'
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())