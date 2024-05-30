from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from products.models import Categories


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "MTech - Главная",
        "content": "Магазин техники MTech",
    }

    return render(request, "main/index.html", context)


def about(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "MTech - О нас",
        "content": "О нас",
    }

    return render(request, "main/about.html", context)
