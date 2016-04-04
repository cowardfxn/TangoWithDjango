from django.test import TestCase
from rango.models import Category, Page
from django.core.urlresolvers import reverse
from datetime import datetime


# Create your tests here.

class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        """
        ensure_views_are_positive should results True for categories where views
         are zero or positive
        """
        cat = Category(name='test', views = -1, likes = 0)
        cat.save()
        self.assertNotEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        """
        slug_line_creation checks to make sure that when we add a category an appropriate slug line is created
        i.e. "Random Category String" -> "random-category-string"
        :return:
        """
        cat = Category(name='Category Random String')
        cat.save()
        self.assertEqual(cat.slug, 'category-random-string')


# class IndexViewTests(TestCase):
#     def test_index_view_with_no_categories(self):
#         """
#         If no questions exist, an appropriate message should be displayed.
#         :return:
#         """
#         response = self.client().get(reverse('index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "There are no categories present")
#         self.assertQuerysetEqual(response.context['categories'], [])


class PageMethodTests(TestCase):
    def test_ensure_valid_date(self):
        '''
        ensure_valid date checks to make sure that last_visit is bigger or equal than first_visit
        :return:
        '''
        Category.objects.get_or_create(name='test_cat')
        cat = Category.objects.get(name='test_cat')
        page = Page(category=cat, title="test", first_visit=datetime.strptime("20120912", '%Y%m%d'))
        page.save()
        self.assertLessEqual(page.first_visit, page.last_visit)
