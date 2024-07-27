from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article,ArticleMedia
import re
import markdown
import textwrap
import base64
import io
from PIL import Image
import numpy as np

def are_images_similar(image_bytes1, image_bytes2, threshold=95):
    img1 = Image.open(io.BytesIO(image_bytes1)).convert("RGB")
    img2 = Image.open(io.BytesIO(image_bytes2)).convert("RGB")
    
    img1 = img1.resize((128, 128))
    img2 = img2.resize((128, 128))

    img1_array = np.array(img1)
    img2_array = np.array(img2)

    difference = np.mean(np.abs(img1_array - img2_array))
    
    print("dif "+ str(float(difference)))
    print("TRESHOLD " + str(float(threshold)))
    print("RES "+str(float(difference) < threshold))
    return float(difference) < threshold

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
        print({
            'news': articles,
            'total_pages': total_pages,
            'current_page': page,
            'page_numbers': page_numbers,
            })
        
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
        try:
            if article.article:
                article.article = remove_whitespace_characters(article.article)
                article.article = markdown.markdown(article.article)
            else:
                article.article = ""
        except:
            article.article = ""

        article.title = remove_whitespace_characters(article.title)
      
        
        media = article.media.all()
        medias = []
        art_media = get_object_or_404(ArticleMedia, article=article, img_main=True)

        for med in media:
            med.is_video = True if med.media_type.startswith("video/") else False
            med.is_image = True if med.media_type.startswith("image/") else False
            print("is_image:"+str(med.is_image))
            if med.is_image == True and are_images_similar(med.file_data,art_media.file_data):
                continue
            else:
                
                medias.append(med)
        article.media_items =  medias
        
        print(article.media_items)
        context = {"article":article}
        return render(requst,"landing/article.html",context=context)
    else:
        return redirect("/authinticate/login/")
    

def serve_media(request, media_id,main_image=None):
    print(bool(main_image))
    if main_image == 1:
        # Fetch the article associated with the given media_id
        article = get_object_or_404(Article, id=media_id)
        
        # Find the main image for the specified article
        media = get_object_or_404(ArticleMedia, article=article, img_main=True)
    else:
        # Fetch the media by ID
        media = get_object_or_404(ArticleMedia, id=media_id)

    # Determine the content type and extension
    content_type = media.media_type
    extension = content_type.split('/')[1]
    
    # Set appropriate content disposition
    content_disposition = 'inline'
    
    # Check if the media is a video or image
    if content_type.startswith('video/'):
        content_disposition = 'inline'
    elif content_type.startswith('image/'):
        content_disposition = 'inline'
    else:
        content_disposition = 'attachment'
    
    # Create the response
    response = HttpResponse(media.file_data, content_type=content_type)
    response['Content-Disposition'] = f'{content_disposition}; filename="media.{extension}"'
    
    return response