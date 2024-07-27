from django.db import models

class Article(models.Model):
    title = models.TextField()
    url = models.TextField()
    date = models.DateTimeField(null=True, blank=True, default=None)
    author = models.CharField(max_length=255, blank=True, null=True)
    brief = models.CharField(max_length=255, blank=True, null=True)
    article = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-id']

class ArticleMedia(models.Model):
    article = models.ForeignKey(Article, related_name='media', on_delete=models.CASCADE)
    file_data = models.BinaryField()
    media_type = models.CharField(max_length=255)
    img_main = models.BooleanField(null=True, blank=True)  # Whether the image is the main one

    class Meta:
        db_table = 'articles_media'
