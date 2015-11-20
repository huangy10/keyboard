import json

from django.test import TestCase, Client
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone

from .models import Emoticon, EmoticonType
from .utils import version_compare
from .views import *
# Create your tests here.


class EmoticonTest(TestCase):

    def setUp(self):
        self.default_type = EmoticonType.objects.create(name='default_type')
        test_file = open('Emoticon/test_files/myface.jpg')
        self.test_file = File(test_file)

    def test_emoticon_creation(self):
        """ Just create
        """
        test_emoticon = Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.assertEqual(test_emoticon.version_no, 0)
        self.assertTrue(test_emoticon.e_type.version_no_expired)
        test_emoticon2 = Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.assertEqual(test_emoticon2.version_no, 1)

    def test_emoticon_get_or_create_deprecated(self):
        """ Test if the get_or_create method is deprecated for Emoticon
        """
        with self.assertRaises(AssertionError):
            Emoticon.objects.get_or_create(icon=self.test_file, code='test', e_type=self.default_type)

    def test_emoticon_filter(self):
        """ Test if filter function ignores inactive emoticons automatically
        """
        Emoticon.objects.create(icon=self.test_file, code='test', is_active=False, e_type=self.default_type)
        self.assertEqual(Emoticon.objects.filter(code='test').count(), 0)
        self.assertEqual(Emoticon.objects.filter(code='test', including_inactive=True).count(), 1)

    def test_emoticon_all(self):
        """ Test if all function ignores inactive emoticons automatically
        """
        Emoticon.objects.create(icon=self.test_file, code='test', is_active=True, e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test', is_active=False, e_type=self.default_type)
        self.assertEqual(Emoticon.objects.all().count(), 1)
        self.assertEqual(Emoticon.objects.all(including_inactive=True).count(), 2)

    def test_emoticon_get_active(self):
        """ Test that the get function can find active emoticons as usual
        """
        Emoticon.objects.create(icon=self.test_file, code='test', is_active=True, e_type=self.default_type)
        Emoticon.objects.get(code='test')

    def test_emoticon_get_inactive(self):
        """ Test that get function ignores inactive emoticons
        """
        Emoticon.objects.create(icon=self.test_file, code='test', is_active=False, e_type=self.default_type)
        with self.assertRaises(ObjectDoesNotExist):
            Emoticon.objects.get(code='test')
        Emoticon.objects.get(code='test', including_inactive=True)


class EmoticonTypeTest(TestCase):

    def setUp(self):
        self.default_type = EmoticonType.objects.create(name='default_type')
        test_file = open('Emoticon/test_files/myface.jpg')
        self.test_file = File(test_file)

    def test_synchronize_with_one_emoticon(self):
        """ Test the synchronize function
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.assertEqual(self.default_type.version_no, 0)
        self.default_type.synchronize()
        self.assertFalse(self.default_type.version_no_expired)
        self.assertEqual(self.default_type.version_no, 1)
        self.assertTrue(Emoticon.objects.get(code='test').is_published)

    def test_synchronized_with_multi_emoticons(self):
        """ Test the synchronize function with multiple emoticons for one single code
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.assertEqual(self.default_type.version_no, 0)
        self.default_type.synchronize()
        self.assertEqual(self.default_type.version_no, 1)
        self.assertTrue(Emoticon.objects.get(code='test').is_published)
        self.assertFalse(Emoticon.objects.get(code='test', is_active=False, including_inactive=True).is_published)

    def test_synchronized_multi_times(self):
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.default_type.synchronize()
        self.assertEqual(self.default_type.version_no, 1)
        # Synchronize again
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.default_type.synchronize()
        self.assertEqual(self.default_type.version_no, 2)
        # Create two new emoticons with different code
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test3', e_type=self.default_type)
        # and synchronize
        self.default_type.synchronize()
        self.assertEqual(self.default_type.version_no, 3)

    def test_available_emoticons_with_different_code(self):
        """ Test the available_emoticons function with different emoticons with different code
        """
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        self.default_type.synchronize()
        self.assertEqual(Emoticon.objects.available_emoticons(self.default_type).count(), 2)

    def test_available_with_update_emoticon(self):
        """ Test the available_emoticons function with different emoticons with different code
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        self.default_type.synchronize()
        available_emoticons = Emoticon.objects.available_emoticons(self.default_type)
        self.assertEqual(available_emoticons.count(), 1)
        emoticon_available = available_emoticons[0]
        self.assertEqual(emoticon_available.version_no, 1)

    def test_available_with_update_emoticon_with_inactive(self):
        """ Test the available_emoticons function with different emoticons with different code
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        self.default_type.synchronize()
        available_emoticons = Emoticon.objects.available_emoticons(self.default_type)
        self.assertEqual(available_emoticons.count(), 1)
        emoticon_available = available_emoticons[0]
        self.assertEqual(emoticon_available.version_no, 0)

    def test_available_with_update_emoticon_with_inactive_with_multi_codes(self):
        """ Test the available_emoticons function with different emoticons with different code
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        self.default_type.synchronize()
        available_emoticons = Emoticon.objects.available_emoticons(self.default_type)
        self.assertEqual(available_emoticons.count(), 2)
        self.assertEqual(available_emoticons[0].version_no, 0)
        self.assertEqual(available_emoticons[1].version_no, 1)

    def test_create_version_synchronization(self):
        """ Test the create_version_synchronization function
        """
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test3', e_type=self.default_type)
        self.default_type.synchronize()
        synchronization_data = self.default_type.version_synchronization
        self.assertEqual(synchronization_data, {
            u'test': 2,
            u'test1': 0,
            u'test3': 0
        })
        # actual_data = [{
        #     'code': u'test', 'version_no': 2
        # }, {
        #     'code': u'test1', 'version_no': 0
        # }, {
        #     'code': u'test3', 'version_no': 0
        # }]
        # self.assertFalse(any(x != y for x, y in zip(synchronization_data, actual_data)))

    def test_create_version_synchronization_with_deletion(self):
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type, is_active=False)
        Emoticon.objects.create(icon=self.test_file, code='test', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        tmp = Emoticon.objects.create(icon=self.test_file, code='test3', e_type=self.default_type)
        self.default_type.synchronize()
        synchronization_data = self.default_type.version_synchronization
        self.assertEqual(synchronization_data, {
            u'test': 1,
            u'test1': 0,
            u'test3': 0
        })
        tmp.is_active = False
        tmp.save()
        self.default_type.synchronize()
        latest_type = EmoticonType.objects.all()[0]
        synchronization_data = latest_type.version_synchronization
        self.assertEqual(synchronization_data, {
            u'test': 1,
            u'test1': 0,
        })


class EmoticonUtilityTest(TestCase):

    def setUp(self):
        self.default_type = EmoticonType.objects.create(name='default_type')
        test_file = open('Emoticon/test_files/myface.jpg')
        self.test_file = File(test_file)
        self.maxDiff = None

    def test_version_compare_added_list(self):
        test1 = Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        test2 = Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        self.default_type.synchronize()
        result = version_compare([
            {
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 0,
                'emoticons': {
                    'test1': 0
                }
            }
        ])
        self.assertEqual(result, {
            'success': True,
            'update_list': [{
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 1,
                'emoticons': [{
                    'code': u'test2',
                    'version_no': 0,
                    'order_weight': 0,
                    'icon_url': test2.icon.url,
                    'description': u'',
                    'operation': 'add'
                }]
            }],
            'deleted_types': []
        })

    def test_version_compare_deleted_list(self):
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type, is_active=False)
        self.default_type.synchronize()
        result = version_compare([
            {
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 0,
                'emoticons': {
                    'test1': 0,
                    'test2': 0
                }
            }
        ])
        self.assertEqual(result, {
            'success': True,
            'update_list': [{
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 1,
                'emoticons': [{
                    'code': u'test2',
                    'operation': 'delete'
                }]
            }],
            'deleted_types': []
        })

    def test_version_compare_change_list(self):
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        test2 = Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        self.default_type.synchronize()
        result = version_compare([
            {
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 0,
                'emoticons': {
                    'test1': 0,
                    'test2': 0
                }
            }
        ])
        self.assertEqual(result, {
            'success': True,
            'update_list': [{
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 1,
                'emoticons': [{
                    'code': u'test2',
                    'version_no': 1,
                    'order_weight': 0,
                    'icon_url': test2.icon.url,
                    'description': u'',
                    'operation': 'change'
                }]
            }],
            'deleted_types': []
        })

    def test_version_compare_deleted_types(self):
        new_type = EmoticonType.objects.create(name='new_type')
        Emoticon.objects.create(icon=self.test_file, code='test1', e_type=new_type)
        Emoticon.objects.create(icon=self.test_file, code='test3', e_type=self.default_type)
        new_type.synchronize()
        self.default_type.synchronize()
        Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        new_type.is_active = False
        new_type.save()
        new_type.synchronize()
        self.default_type.synchronize()
        result = version_compare([
            {
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 2,
                'emoticons': {
                    'test2': 0,
                    'test3': 0
                }
            }, {
                'emoticon_type_id': new_type.id,
                'emoticon_version_no': 0,
                'emoticons': {
                    'test1': 0,
                }
            }])
        self.assertEqual(result, {
            'success': True,
            'update_list': [],
            'deleted_types': [new_type.id]
        })

    def test_version_compare_get_all(self):
        test1 = Emoticon.objects.create(icon=self.test_file, code='test1', e_type=self.default_type)
        test2 = Emoticon.objects.create(icon=self.test_file, code='test2', e_type=self.default_type)
        self.default_type.synchronize()
        result = version_compare([
            {
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': -1,
                'emoticons': {}
            }
        ])
        self.assertEqual(result, {
            'success': True,
            'update_list': [{
                'emoticon_type_id': self.default_type.id,
                'emoticon_version_no': 1,
                'emoticons': [{
                    'code': u'test1',
                    'version_no': 0,
                    'order_weight': 0,
                    'icon_url': test1.icon.url,
                    'description': u'',
                    'operation': 'add'
                }, {
                    'code': u'test2',
                    'version_no': 0,
                    'order_weight': 0,
                    'icon_url': test2.icon.url,
                    'description': u'',
                    'operation': 'add'
                }]
            }],
            'deleted_types': []
        })


class EmoticonViewTest(TestCase):

    def setUp(self):
        self.default_type = EmoticonType.objects.create(name='default_type')
        test_file = open('Emoticon/test_files/myface.jpg')
        self.test_file = File(test_file)
        self.default_emoticon = Emoticon.objects.create(
            e_type=self.default_type, icon=self.test_file, code='default_test')
        self.client = Client()
        self.user = get_user_model().objects.create(username='test_user', password='test_password')
        self.user.set_password('test_password')
        self.user.save()

    def test_check_update_accessibility(self):
        response = self.client.post('/emoticons/check_update',
                                    json.dumps({
                                        'version_info': [
                                            dict(emoticon_type_id=self.default_type.id,
                                                 emoticon_version_no=0,
                                                 emoticons={}), ],
                                        'username': 'test_user',
                                        'password': 'test_password',
                                        }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_check_update_without_identification(self):
        response = self.client.post('/emoticons/check_update',
                                    json.dumps({'version_info': json.dumps([
                                        dict(emoticon_type_id=self.default_type.id,
                                             emoticon_version_no=0,
                                             emoticons={}), ]),
                                        }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result, dict(success=False, reason="Permission Denied"))

    def test_all_emoticon_types_accessibility(self):
        response = self.client.post('/emoticons/all',
                                    json.dumps(dict(username='test_user', password='test_password')),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_all_emoticon_types_without_identification(self):
        response = self.client.post('/emoticons/all', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result, dict(success=False, reason="Permission Denied"))

    def test_all_emoticons_types_result(self):
        response = self.client.post('/emoticons/all',
                                    json.dumps(dict(username='test_user', password='test_password')),
                                    content_type='application/json')
        result = json.loads(response.content)
        self.maxDiff = None
        self.assertEqual(result, dict(success=True, emoticon_types=[
            dict(name=self.default_type.name,
                 version_no=self.default_type.version_no,
                 order_weight=self.default_type.order_weight,
                 id=self.default_type.id,
                 time_mark_start_hour=self.default_type.time_mark_start_hour,
                 time_mark_end_hour=self.default_type.time_mark_end_hour,
                 time_mark_start_min=self.default_type.time_mark_end_min,
                 time_mark_end_min=self.default_type.time_mark_end_min),
        ]))

    def test_usage_report_types_accessibility(self):
        response = self.client.post('/emoticons/report',
                                    json.dumps(dict(username='test_user',
                                                    password='test_password',
                                                    emoticon_code='default_test',
                                                    version_no=0,
                                                    use_time=timezone.now().strftime("%Y-%m-%d %H:%M:%S"))),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_usage_report_types_without_identification(self):
        response = self.client.post('/emoticons/report',
                                    json.dumps(dict(emoticon_code='default_test', version_no=0,
                                                    use_time=timezone.now().strftime("%Y-%m-%d %H:%M:%S"))),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result, dict(success=False, reason="Permission Denied"))