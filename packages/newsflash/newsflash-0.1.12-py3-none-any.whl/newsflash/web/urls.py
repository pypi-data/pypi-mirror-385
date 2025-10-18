from django.urls import path, include


urlpatterns = [
    path("", include("newsflash.web.app.urls")),
    path("accounts/", include("newsflash.web.accounts.urls")),
]
