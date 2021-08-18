from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth.models import User
from snippets.models import Script
from scripts.serializers import ScriptSerializer


SCRIPTS_URL = '/scripts/'


def create_sample_script(owner, name='TestScript', snippets=''):
    instance = Script.objects.create(owner=owner,
                                     name=name,
                                     snippets=snippets)
    return instance


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

    def test_listing_script(self):
        """Test listing script objects"""
        create_sample_script(self.user, name='TestScript1')
        create_sample_script(self.user, name='TestScript2')

        res = self.client.get(SCRIPTS_URL)
        expected = ScriptSerializer(Script.objects.all().order_by('id'),
                                    many=True).data

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, expected)

    def test_getting_script_detail(self):
        script = create_sample_script(self.user)

        detail_url = f'{SCRIPTS_URL}{script.id}'
        res = self.client.get(path=detail_url)

        expected = ScriptSerializer(script).data
        self.assertEqual(res.data, expected)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
