from http.client import responses

from django.test import TestCase
from rest_framework.status import HTTP_201_CREATED
from rest_framework.test import  APITestCase
from .models import Item
from rest_framework import  status
"""
APITestCase POST item creation
"""
class PostItemTestCase(APITestCase):
    """
    Setup part with general data
    """
    def setUp(self):
        self.url = "/api/items/create/"
        self.data = {
            'title':'ApiTestPOSTmethod',
            'description':'POST method Post method',
        }
    """
    Test with a valid data. Compares status code, title, description
    """
    def test_create_data_valid(self):
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'ApiTestPOSTmethod')
        self.assertEqual(response.data['description'], 'POST method Post method')
        self.assertEqual(Item.objects.count(), 1)
        item = Item.objects.first()
        self.assertEqual(item.title, 'ApiTestPOSTmethod')
        self.assertEqual(item.description, 'POST method Post method')
    """
    Test creating item without title
    """
    def test_create_data_without_title(self):
        invalid_data = {
            'description': 'POST method Post method'
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertEqual(Item.objects.count(), 0)
    """
    Test creating item with overflowed title
    """
    def test_create_data_overflowed_title(self):
        over_title = 'aa' * 100
        overflowed_data = {
            'title': over_title,
            'description': 'This test provides overflow'
        }
        response = self.client.post(self.url, overflowed_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertEqual(Item.objects.count(), 0)
    """
    Test creating multiply items
    """
    def test_creating_multiply_items(self):
        first_item = {
            'title': 'TestItem1',
            'description': 'This is first item in test multiply items'
        }
        second_item = {
            'title': 'TestItem2',
            'description': 'This is a second item in test multiply items'
        }
        first_response = self.client.post(self.url, first_item, format='json')
        second_response = self.client.post(self.url, second_item, format= 'json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
    """
    Test GET selected item
    """


