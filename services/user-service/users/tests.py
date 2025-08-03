from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.urls import reverse
from users.models import User

class UserViewSetTest(APITestCase):
    def test_create_user_via_api(self):
        url = reverse('user-list')  # DRF router name for UserViewSet list/create
        data = {
            "username": "apiuser",
            "email": "apiuser@example.com",
            "password": "strongpassword",
            "location": "London",
            "age": 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        # Password should not be in response
        self.assertNotIn('password', response.data)

        # Check user is in DB with hashed password
        user = User.objects.get(username=data['username'])
        self.assertTrue(user.check_password(data['password']))
