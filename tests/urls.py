from django.urls import include, path

urlpatterns = [
    path("docs/", include("md_docs.urls")),
]
