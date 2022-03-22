import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import Profile

class SignupTestCase(APITestCase):

    def test_signup(self):
        data = {
            "email":"test@gmail.com",
            "password": "test@1",
            "firstname": "Test",
            "lastname": "Case",
            "account_type": "Individual",
            "business_name":"TestJust"
        }
        response = self.client.post("/api/users/register", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)