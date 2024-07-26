from django.db import models

class Article(models.Model):
    img_url = models.TextField(blank=True, null=True)
    title = models.TextField()
    url = models.TextField()
    date = models.DateTimeField(null=True, blank=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    brief = models.CharField(max_length=255, blank=True, null=True)
    article = models.TextField()

    class Meta:
        db_table = 'articles'
        ordering = ['-id']

class ArticleMedia(models.Model):
    article = models.ForeignKey(Article, related_name='media', on_delete=models.CASCADE)
    file_data = models.BinaryField()
    media_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'articles_media'
