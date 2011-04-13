from datetime import datetime, timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError

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
    def setUp(self):
        objects = [
            {'title': 'Future Unpublished', 'pub_date': datetime.now() + timedelta(1), 'published': False},
            {'title': 'Future Published',   'pub_date': datetime.now() + timedelta(1), 'published': True},
            {'title': 'Past Unpublished',   'pub_date': datetime.now() - timedelta(1), 'published': False},
            {'title': 'Past Published',     'pub_date': datetime.now() - timedelta(1), 'published': True},
        ]
        
        for object in objects:
            Thought.objects.create(**object)
            
    def test_unpublished_returns_past_published(self):
        self.assertItemsEqual(Thought.objects.published(), Thought.objects.filter(published=True, pub_date__lte=datetime.now()))