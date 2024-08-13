from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("<int:page>", views.index, name="index_paginated"),
    path("/source/<str:source>", views.index, name="spec_source"),
    path("articles/<int:id>", views.article, name="article"),
    path("media/<int:media_id>/", views.serve_media, name="serve_media"),
    path(
        "media/<int:media_id>/<int:main_image>", views.serve_media, name="serve_media"
    ),
]
