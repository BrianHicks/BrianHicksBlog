import datetime

import markdown
from django.db import models

# Create your models here.

class ThoughtManager(models.Manager):
    def published(self):
        return self.filter(published=True)

class Thought(models.Model):
    '''
    A thought (blog post)
    '''
    title = models.CharField(max_length=80)
    slug = models.SlugField()
    
    published = models.BooleanField(default=False)
    
    pub_date = models.DateTimeField()
    
    content = models.TextField(help_text="Thought, in Markdown Format")
    html_content = models.TextField(blank=True)
    
    objects = ThoughtManager()
    
    def render_markdown(self, input):
        # turn input into unicode string
        input = unicode(input)
        return markdown.markdown(input, ['codehilite', 'footnotes'])
        
    def save(self, *args, **kwargs):
        self.html_content = self.render_markdown(self.content)
        super(Thought, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        return '%s/%s/%s/%s/' % (self.pub_date.year, self.pub_date.month, self.pub_date.day, self.slug)
        
    def __unicode__(self):
        return self.title