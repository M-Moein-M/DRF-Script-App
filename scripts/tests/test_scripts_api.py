from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth.models import User
from snippets.models import Script


SCRIPTS_URL = '/scripts/'


class ScriptApiTest(TestCase):
    """Testing script api"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpasswd')
        self.client.force_authenticate(user=self.user)

    def test_creating_script(self):
        """Test creating script object"""
        payload = {
            'owner': self.user,
            'name': 'TestScript',
            'snippets': '',
        }

        res = self.client.post(SCRIPTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Script.objects.filter(id=res.data['id']).exists())
        script = Script.objects.get(id=res.data['id'])
        for k in payload:
            self.assertEqual(payload[k], getattr(script, k))
