import markdown

from django.db import models

# Create your models here.

class Thought(models.Model):
    '''
    A thought (blog post)
    '''
    content = models.TextField(help_text="Thought, in Markdown Format")
    html_content = models.TextField()
    
    def render_markdown(self, input):
        # turn input into unicode string
        input = unicode(input)
        return markdown.markdown(input, ['codehilite'])
        
    def save(self, *args, **kwargs):
        self.html_content = self.render_markdown(self.content)
        super(Thought, self).save(*args, **kwargs)