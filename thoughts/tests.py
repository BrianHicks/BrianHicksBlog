from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from thoughts.models import Thought

class ThoughtTest(TestCase):
    def setUp(self):
        self.blank_t = Thought()
        
        self.valid_t = Thought()
        self.valid_t.pub_date = datetime(2011, 1, 1, 0, 0, 0, 0)
        self.valid_t.name = 'Test'
        self.valid_t.slug = 'test'
        
        self.fields = Thought._meta.fields
    
    # attributes
    def test_fields_exist(self):
        fields = ['content', 'html_content', 'title', 'slug', 'pub_date']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields], '"%s" not in fields for Thought' % field)        
    
    def test_fields_required(self):
        required = ['content', 'title', 'slug', 'pub_date']
        not_required = ['html_content']
        try:
            self.blank_t.full_clean()
        except ValidationError as e:
            for field in required:
                self.assertRegexpMatches(e.message_dict[field][0], 'This field cannot be (blank|null).')
            for field in not_required:
                self.assertEqual(e.message_dict.get(field), None)
    
    def test_help_text_exists(self):
        fields = ['content']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields if f.help_text != ''], '"%s" does not have help text.')
            
    def test_name_validation(self):
        self.blank_t.title = 'a'*81
        try:
            self.blank_t.full_clean()
        except ValidationError as e:
            self.assertEqual(e.message_dict['title'], [u'Ensure this value has at most 80 characters (it has 81).'])
    
    # render_markdown
    def test_render_markdown_returns_unicode(self):
        result = self.valid_t.render_markdown('A test string')
        self.assertTrue(isinstance(result, unicode), 'render_markdown did not return a string')
        result = self.valid_t.render_markdown(0)
        self.assertTrue(isinstance(result, unicode), 'render_markdown did not return a string')
    
    def test_render_markdown_returns_html(self):
        result = self.valid_t.render_markdown('A *test* string')
        self.assertEqual(result, "<p>A <em>test</em> string</p>")
        
    def test_render_markdown_renders_python_code(self):
        result = self.valid_t.render_markdown('\t:::python\n\ttest_var = "test"')
        self.assertEqual(result, '<div class="codehilite"><pre><span class="n">test_var</span> <span class="o">=</span> <span class="s">&quot;test&quot;</span>\n</pre></div>')
        
    def test_render_markdown_renders_footnotes(self):
        result = self.valid_t.render_markdown('Footnote[^label]\n\n[^label]: Footnote')
        self.assertEqual(result, '<p>Footnote<sup id="fnref:label"><a href="#fn:label" rel="footnote">1</a></sup></p>\n<div class="footnote">\n<hr />\n<ol>\n<li id="fn:label">\n<p>Footnote\n&#160;<a href="#fnref:label" rev="footnote" title="Jump back to footnote 1 in the text">&#8617;</a></p>\n</li>\n</ol>\n</div>')
        
    # str
    def test_str_not_unset(self):
        self.assertNotEqual(str(self.valid_t), 'Thought object')
        
    def test_str_is_title(self):
        self.assertEqual(str(self.valid_t), self.valid_t.title)
        
    # get_absolute_url
    def test_absolute_url_is_not_blank(self):
        self.assertNotEqual(self.valid_t.get_absolute_url(), '')
        
    def test_absolute_url_is_y_m_d_slug(self):
        self.assertEqual(self.valid_t.get_absolute_url(), '2011/1/1/test/')
    
    # save
    def test_render_markdown_on_save(self):
        self.valid_t.content = 'A *test* string'
        self.valid_t.save()
        self.assertEqual(self.valid_t.html_content, "<p>A <em>test</em> string</p>")
        
        
class ThoughtManagerTest(TestCase):
    @classmethod
    def setUpClass(self):
        self.objects = [
            {'title': 'Future Unpublished', 'pub_date': datetime.now() + timedelta(1), 'published': False},
            {'title': 'Future Published',   'pub_date': datetime.now() + timedelta(1), 'published': True},
            {'title': 'Past Unpublished',   'pub_date': datetime.now() - timedelta(1), 'published': False},
            {'title': 'Past Published',     'pub_date': datetime.now() - timedelta(1), 'published': True},
        ]
        
        for object in self.objects:
            Thought.objects.create(**object)
            
    def test_published_returns_objects(self):
        self.assertGreater(Thought.objects.published(), 0)
    
    def test_published_returns_past_published(self):
        pass
        #self.assertItemsEqual(Thought.objects.published(), Thought.objects.filter(published=True).order_by('-pub_date'))
        
    @classmethod
    def tearDownClass(self):
        for object in self.objects:
            Thought.objects.get(title=object['title']).delete()

class ArchiveCommon(object):
    @classmethod
    def setUpClass(self):
        self.test_objects = []
        for i in range(50):
            self.test_objects.append(Thought.objects.create(title=i, slug=i, pub_date=datetime.now() - timedelta(i * 2), published=True))
            
    def setUp(self):
        self.client = Client()
        self.url = ''
        
    def test_responds_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
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


class ThoughtsIndexTest(ArchiveCommon, TestCase):
    def setUp(self, *args, **kwargs):
        super(ThoughtsIndexTest, self).setUp(*args, **kwargs)
        self.url = reverse('thoughts')
        
        
class ThoughtsByYearTest(ArchiveCommon, TestCase):
    def setUp(self, *args, **kwargs):
        super(ThoughtsByYearTest, self).setUp(*args, **kwargs)
        self.url = response = reverse('thoughts_year', args=[datetime.now().year])
            
class ThoughtsByMonthTest(ArchiveCommon, TestCase):
    def setUp(self, *args, **kwargs):
        super(ThoughtsByMonthTest, self).setUp(*args, **kwargs)
        now = datetime.now()
        self.url = reverse('thoughts_month', args=[now.year, now.strftime('%b')])
        
class ThoughtsByDayTest(ArchiveCommon, TestCase):
    @classmethod
    def setUpClass(self):
        ''' we need more data per day here to get it to paginate, so this is overridden '''
        self.test_objects = []
        for i in range(50):
            self.test_objects.append(Thought.objects.create(title=i, slug=i, pub_date=datetime.now(), published=True))
            
    def setUp(self, *args, **kwargs):
        super(ThoughtsByDayTest, self).setUp(*args, **kwargs)
        now = datetime.now()
        self.url = reverse('thoughts_day', args=[now.year, now.strftime('%b'), now.day])