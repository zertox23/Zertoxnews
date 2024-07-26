from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article,ArticleMedia
import re
import markdown
import textwrap
import base64

def image_to_base64(images):
    for image in images:
        encoded_string = base64.b64encode(image).decode('utf-8')
        return encoded_string

def remove_whitespace_characters(text):
    """Remove newline, carriage return, and tab characters from the string."""
    text = text.replace("\\r\\n\\t\\t","")
    text = text.replace("\\t","")
    text = text.replace("\\n\\n","\n \n")
    return text


def index(request,page:int=1):
    if request.user.is_authenticated:
        # Assuming 10 articles per page
        articles_per_page = 7
        start = (page - 1) * articles_per_page
        end = start + articles_per_page
        articles = Article.objects.all().order_by('-id')[start:end]
        for article in articles:
            article.title = remove_whitespace_characters(article.title)
        # Total number of pages
        total_articles = Article.objects.count()
        total_pages = (total_articles + articles_per_page - 1) // articles_per_page
        page_numbers = range(1, total_pages + 1)
        return render(request, 'landing/landing.html', {
            'news': articles,
            'total_pages': total_pages,
            'current_page': page,
            'page_numbers': page_numbers,
            })
    else:
        return redirect("login")

def article(requst,id:int):
    if requst.user.is_authenticated:
        article = Article.objects.get(id=id)
        article.title = remove_whitespace_characters(article.title)
        article.article = remove_whitespace_characters(article.article)
        with open("data.md","w") as f:
            f.write(article.article) 

        article.article = markdown.markdown(article.article)
        images = article.media.all()
        article.images = images
        context = {"article":article}
        return render(requst,"landing/article.html",context=context)
    else:
        return redirect("/authinticate/login/")
    

def serve_image(request, media_id):
    media = get_object_or_404(ArticleMedia, id=media_id)
    if media.media_type == "image":
        media.media_type = "image/png"
    response = HttpResponse(media.file_data, content_type=media.media_type)
    response['Content-Disposition'] = f'inline; filename="image.{media.media_type.split("/")[1]}"'
    return response