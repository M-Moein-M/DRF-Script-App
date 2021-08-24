from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth.models import User
from snippets.models import Script, Snippet
from scripts.serializers import ScriptSerializer

SCRIPTS_URL = '/scripts/'


def get_script_detail_url(pk):
    return f'{SCRIPTS_URL}{pk}'


def create_sample_snippet(owner, title, code):
    instance = Snippet.objects.create(owner=owner,
                                      title=title,
                                      code=code)
    return instance


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

        detail_url = get_script_detail_url(script.id)
        res = self.client.get(path=detail_url)

        expected = ScriptSerializer(script).data
        self.assertEqual(res.data, expected)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_patching_script_detail(self):
        payload = {'name': 'updated_name'}

        script = create_sample_script(owner=self.user)

        detail_url = get_script_detail_url(script.id)
        res = self.client.patch(detail_url, data=payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        script.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(script, key, None), payload[key])

    def test_deleting_script_detail(self):
        script = create_sample_script(owner=self.user)

        detail_url = get_script_detail_url(script.id)
        res = self.client.delete(detail_url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Script.objects.filter(id=script.id).exists())


class ScriptApiSnippetsFieldTest(TestCase):
    """Testing snippets field for script objects"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpasswd')
        self.client.force_authenticate(user=self.user)

    def test_creating_script_valid_snippets(self):
        snippet1 = create_sample_snippet(owner=self.user,
                                         title='Title1',
                                         code='print(datetime.datetime.now())')
        snippet2 = create_sample_snippet(owner=self.user,
                                         title='Title2',
                                         code="print('end of program')")

        payload = {
            'owner': self.user,
            'name': 'TestScript',
            'snippets': f'{snippet1.id},{snippet2.id}',
        }
        res = self.client.post(path=SCRIPTS_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Script.objects.filter(id=res.data['id']).exists())
        script = Script.objects.get(id=res.data['id'])
        for k in payload:
            self.assertEqual(payload[k], getattr(script, k))

    def test_creating_script_invalid_snippets(self):
        snippet1 = create_sample_snippet(owner=self.user,
                                         title='Title1',
                                         code='print(datetime.datetime.now())')
        snippet2 = create_sample_snippet(owner=self.user,
                                         title='Title2',
                                         code="print('end of program')")

        invalid_id = snippet1.id + snippet2.id
        payload = {
            'owner': self.user,
            'name': 'TestScript',
            'snippets': f'{snippet1.id},{snippet2.id},{invalid_id}',
        }

        res = self.client.post(path=SCRIPTS_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patching_script_valid_snippets(self):
        snippet1 = create_sample_snippet(owner=self.user,
                                         title='Title1',
                                         code='print(datetime.datetime.now())')
        snippet2 = create_sample_snippet(owner=self.user,
                                         title='Title2',
                                         code="print('end of program')")
        script = create_sample_script(owner=self.user,
                                      snippets=f'{snippet1.id}')

        payload = {'snippets': f'{snippet2.id},{snippet1.id}'}
        res = self.client.patch(get_script_detail_url(script.id), payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        script.refresh_from_db()
        for key, val in payload.items():
            self.assertEqual(getattr(script, key, None), payload[key])

    def test_patching_script_invalid_snippets(self):
        snippet1 = create_sample_snippet(owner=self.user,
                                         title='Title1',
                                         code='print(datetime.datetime.now())')
        script = create_sample_script(owner=self.user,
                                      snippets=f'{snippet1.id}')

        payload = {'snippets': f'{200},{snippet1.id}'}
        res = self.client.patch(get_script_detail_url(script.id), payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
