from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth.models import User
from snippets.models import Script, Snippet
from scripts.serializers import ScriptSerializer, ScriptDetailSerializer

SCRIPTS_URL = '/scripts/'


def get_script_detail_url(pk):
    return f'{SCRIPTS_URL}{pk}'


def create_sample_snippet(owner, code, title='SnippetTitle', n=1):
    ret = list()
    for i in range(n):
        ret.append(Snippet.objects.create(owner=owner,
                                          title=f'{title}-{i}',
                                          code=f'{code} #{i}'))
    return ret[0] if n == 1 else ret


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
        snippet1, snippet2 = create_sample_snippet(
            owner=self.user,
            code='print(datetime.datetime.now())',
            n=2)
        script = create_sample_script(self.user,
                                      snippets=f'{snippet1.id},{snippet2.id}')

        detail_url = get_script_detail_url(script.id)
        res = self.client.get(path=detail_url)

        expected = ScriptDetailSerializer(script).data
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
        snippet1, snippet2 = create_sample_snippet(
            owner=self.user,
            code='print(datetime.datetime.now())',
            n=2)

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
        snippet1, snippet2 = create_sample_snippet(
            owner=self.user,
            code='print(datetime.datetime.now())',
            n=2)

        invalid_id = snippet1.id + snippet2.id
        payload = {
            'owner': self.user,
            'name': 'TestScript',
            'snippets': f'{snippet1.id},{snippet2.id},{invalid_id}',
        }

        res = self.client.post(path=SCRIPTS_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patching_script_valid_snippets(self):
        snippet1, snippet2 = create_sample_snippet(
            owner=self.user,
            code='print(datetime.datetime.now())',
            n=2)
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


class TestAuthRestrictedRequest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser',
                                             email='testuser@test.com',
                                             password='testpasswd')

    def test_creating_script_not_authenticated_user(self):
        payload = {
            'owner': self.user,
            'name': 'TestScript',
            'snippets': '',
        }
        res = self.client.post(SCRIPTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patching_script_not_authenticated_user(self):
        script = create_sample_script(self.user)
        payload = {
            'name': 'PatchedName'
        }

        res = self.client.patch(get_script_detail_url(script.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patching_script_not_owner_user(self):
        script = create_sample_script(self.user)
        payload = {
            'name': 'PatchedName'
        }
        user2 = User.objects.create_user(username='testuser2',
                                         email='testuser2@test.com',
                                         password='testpasswd2')
        self.client.force_authenticate(user=user2)
        res = self.client.patch(get_script_detail_url(script.id), payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_script_not_authenticated_user(self):
        script = create_sample_script(self.user)

        res = self.client.delete(get_script_detail_url(script.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_deleting_script_not_owner_user(self):
        script = create_sample_script(self.user)

        user2 = User.objects.create_user(username='testuser2',
                                         email='testuser2@test.com',
                                         password='testpasswd2')
        self.client.force_authenticate(user=user2)
        res = self.client.delete(get_script_detail_url(script.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
