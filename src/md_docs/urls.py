from django.urls import path

from . import views

app_name = "md_docs"

urlpatterns = [
    path("", views.docs_page, name="docs-index"),
    path("<path:page>", views.docs_page, name="docs-page"),
]
