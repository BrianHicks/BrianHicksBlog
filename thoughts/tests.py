from django.test import TestCase

from thoughts.models import Thought

class ThoughtTest(TestCase):
    def setUp(self):
        self.t = Thought()
        self.fields = Thought._meta.fields
    
    # attributes
    def test_fields_exist(self):
        fields = ['content', 'html_content']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields], '"%s" not in fields for Thought' % field)
            
    def test_help_text_exists(self):
        fields = ['content']
        for field in fields:
            self.assertTrue(field in [f.name for f in self.fields if f.help_text != ''], '"%s" does not have help text.')
            
    # render_markdown
    def test_render_markdown_returns_unicode(self):
        result = self.t.render_markdown('A test string')
        self.assertTrue(isinstance(result, unicode), 'render_markdown did not return a string')
        result = self.t.render_markdown(0)
        self.assertTrue(isinstance(result, unicode), 'render_markdown did not return a string')
    
    def test_render_markdown_returns_html(self):
        result = self.t.render_markdown('A *test* string')
        self.assertEqual(result, "<p>A <em>test</em> string</p>")
        