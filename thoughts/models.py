import markdown

from django.db import models

# Create your models here.

class Thought(models.Model):
    '''
    A thought (blog post)
    '''
    title = models.CharField(max_length=80)
    slug = models.SlugField()
    
    pub_date = models.DateTimeField()
    
    content = models.TextField(help_text="Thought, in Markdown Format")
    html_content = models.TextField(blank=True)
    
    def render_markdown(self, input):
        # turn input into unicode string
        input = unicode(input)
        return markdown.markdown(input, ['codehilite', 'footnotes'])
        
    def save(self, *args, **kwargs):
        self.html_content = self.render_markdown(self.content)
        super(Thought, self).save(*args, **kwargs)