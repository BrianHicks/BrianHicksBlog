from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from thoughts.models import Thought

class ViewCommon(object):
    @classmethod
    def setUpClass(self):
        self.client = Client()
        self.url = ''
    
    def setUp(self):
        self.response = self.client.get(self.url)
        
    def test_responds_200(self):
        self.assertEqual(self.response.status_code, 200, '%s returned %s' % (self.url, self.response.status_code))


class ArchiveCommon(ViewCommon):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        super(ArchiveCommon, self).setUpClass(*args, **kwargs)
        self.test_objects = []
        for i in range(50):
            self.test_objects.append(Thought.objects.create(title=i, slug=i, pub_date=datetime.now() - timedelta(i * 2), published=True))
        
    def test_context_is_correct(self, extra=[]):
        response = self.client.get(self.url)
        context_dictionary = response.context_data
        context_variables = ['thought_list', 'paginator', 'page_obj', 'date_list'] + extra
        for var in context_variables:
            self.assertIn(var, context_dictionary)
            self.assertNotEqual(context_dictionary.get(var, ''), '')
            
    def test_is_paginated(self):
        response = self.client.get(self.url)
        is_paginated = response.context_data.get('is_paginated', False)
        self.assertTrue(is_paginated)
        
    def test_has_thoughts(self):
        response = self.client.get(self.url)
        thoughts = response.context_data['thought_list']
        self.assertGreater(len(thoughts), 0)
    
    @classmethod
    def tearDownClass(self):
        for object in self.test_objects:
            object.delete()