from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from thoughts.models import Thought

from thoughts.test_helpers import ArchiveCommon, ViewCommon

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
        '''fields shouldn't go missing.'''
        fields = ['content', 'html_content', 'title', 'slug', 'pub_date']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields], '"%s" not in fields for Thought' % field)        
    
    def test_fields_required(self):
        '''some fields are required'''
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
        '''some fields should have help attached'''
        fields = ['content']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields if f.help_text != ''], '"%s" does not have help text.')
            
    def test_name_validation(self):
        '''titles should be no more than 80 characters long'''
        self.blank_t.title = 'a'*81
        try:
            self.blank_t.full_clean()
        except ValidationError as e:
            self.assertEqual(e.message_dict['title'], [u'Ensure this value has at most 80 characters (it has 81).'])
    
    # render_markdown
    def test_render_markdown_returns_unicode(self):
        '''render_markdown() should return a string (unicode or str, we'll render either way)'''
        result = self.valid_t.render_markdown('A test string')
        self.assertTrue(isinstance(result, basestring), 'render_markdown did not return a string')
        result = self.valid_t.render_markdown(0)
        self.assertTrue(isinstance(result, basestring), 'render_markdown did not return a string')
    
    def test_render_markdown_returns_html(self):
        '''markdown returns html. Just a sanity check.'''
        result = self.valid_t.render_markdown('A *test* string')
        self.assertEqual(result, "<p>A <em>test</em> string</p>")
        
    def test_render_markdown_renders_python_code(self):
        '''python should be highlighted (the pygments plugin should be enabled)'''
        result = self.valid_t.render_markdown('\t:::python\n\ttest_var = "test"')
        self.assertEqual(result, '<div class="codehilite"><pre><span class="n">test_var</span> <span class="o">=</span> <span class="s">&quot;test&quot;</span>\n</pre></div>')
        
    def test_render_markdown_renders_footnotes(self):
        '''footnotes should be rendered (plugin enabled)'''
        result = self.valid_t.render_markdown('Footnote[^label]\n\n[^label]: Footnote')
        self.assertEqual(result, '<p>Footnote<sup id="fnref:label"><a href="#fn:label" rel="footnote">1</a></sup></p>\n<div class="footnote">\n<hr />\n<ol>\n<li id="fn:label">\n<p>Footnote\n&#160;<a href="#fnref:label" rev="footnote" title="Jump back to footnote 1 in the text">&#8617;</a></p>\n</li>\n</ol>\n</div>')
        
    # str
    def test_str_not_unset(self):
        '''we're not returning the default for __unicode__'''
        self.assertNotEqual(unicode(self.valid_t), 'Thought object')
        self.assertNotEqual(str(self.valid_t), 'Thought object')
        
    def test_str_is_title(self):
        '''we want to return the title for __unicode___'''
        self.assertEqual(unicode(self.valid_t), self.valid_t.title)
        self.assertEqual(str(self.valid_t), self.valid_t.title)
        
    # get_absolute_url
    def test_absolute_url_is_not_blank(self):
        '''absolute URL should never be blank, yo!'''
        self.assertNotEqual(self.valid_t.get_absolute_url(), '')
        
    def test_absolute_url_is_y_m_d_slug(self):
        '''the title says it all here.'''
        self.assertEqual(self.valid_t.get_absolute_url(), '2011/1/1/test/')
    
    # save
    def test_render_markdown_on_save(self):
        '''just to make sure the markdown is rendered on *every* save'''
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

# archive views

class ThoughtsIndexTest(ArchiveCommon, TestCase):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        super(ThoughtsIndexTest, self).setUpClass(*args, **kwargs)
        self.url = reverse('thoughts')
        
        
class ThoughtsByYearTest(ArchiveCommon, TestCase):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        super(ThoughtsByYearTest, self).setUpClass(*args, **kwargs)
        self.url = reverse('thoughts_year', args=[datetime.now().year])
        
            
class ThoughtsByMonthTest(ArchiveCommon, TestCase):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        super(ThoughtsByMonthTest, self).setUpClass(*args, **kwargs)
        now = datetime.now()
        self.url = reverse('thoughts_month', args=[now.year, now.strftime('%b')])
        
        
class ThoughtsByDayTest(ArchiveCommon, TestCase):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        ''' we need more data per day here to get it to paginate, so this is overridden '''
        super(ThoughtsByDayTest, self).setUpClass(*args, **kwargs)
        
        now = datetime.now()
        self.url = reverse('thoughts_day', args=[now.year, now.strftime('%b'), now.day])
        
        self.test_objects = []
        for i in range(50):
            self.test_objects.append(Thought.objects.create(title=i, slug=i, pub_date=datetime.now(), published=True))
            
# detail views

class ThoughtDetailTest(ViewCommon, TestCase):
    @classmethod
    def setUpClass(self, *args, **kwargs):
        super(ThoughtDetailTest, self).setUpClass(*args, **kwargs)
        
        now = datetime.now()
        
        self.thought = Thought.objects.create(title='Testing detail view', slug='testing-detail-view', pub_date=now, published=True)
        self.url = reverse('thought', args=[now.year, now.strftime('%b'), now.day, self.thought.slug])
        
    @classmethod
    def tearDownClass(self):
        self.thought.delete()
        
    def test_context_is_correct(self, extra=[]):
        response = self.client.get(self.url)
        context_dictionary = response.context_data
        context_variables = ['thought', 'object']
        for var in context_variables:
            self.assertIn(var, context_dictionary)
            self.assertNotEqual(context_dictionary.get(var, ''), '')