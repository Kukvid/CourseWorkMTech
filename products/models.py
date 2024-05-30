from django.db import models
from decimal import Decimal
from abc import ABC, abstractmethod

from django.contrib.postgres.search import SearchVector, SearchQuery, \
    SearchRank, SearchHeadline

from django.shortcuts import get_list_or_404
from django.urls import reverse


class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")

    class Meta:
        db_table = "category"
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(upload_to="products_images", blank=True, null=True, verbose_name="Изображение")
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена")
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name="Скидка в процентах")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    category = models.ForeignKey(to=Categories, on_delete=models.PROTECT, verbose_name="Категория")

    class Meta:
        db_table = "product"
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ("id",)

    def __str__(self) -> str:
        return f"{self.name} Количество - {self.quantity}"

    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"product_slug": self.slug})

    def display_id(self):
        return f"{self.id:05}"

    def round_half_up(self, n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier + Decimal(0.5)) / multiplier

    def sell_price(self):
        if self.discount:
            return self.round_half_up(self.price - self.price * self.discount / 100, 2)
        return self.price


class IProductFilterStrategy(ABC):
    @abstractmethod
    def filter(self, products):
        pass


class OnSaleFilterStrategy(IProductFilterStrategy):
    def filter(self, products):
        return products.filter(discount__gt=0)


class CategoryFilterStrategy(IProductFilterStrategy):
    def __init__(self, category_slug):
        self.category_slug = category_slug

    def filter(self, products):
        return products.filter(category__slug=self.category_slug)


class SearchFilterStrategy(IProductFilterStrategy):
    def __init__(self, query):
        self.query = query

    def q_search(self):
        if self.query.isdigit() and len(self.query) <= 5:
            return Products.objects.filter(id=int(self.query))

        vector = SearchVector("name", "description")
        query = SearchQuery(self.query)

        result = Products.objects.annotate(rank=SearchRank(vector, query)) \
            .filter(rank__gt=0) \
            .order_by("-rank")
        result = result.annotate(headline=SearchHeadline("name",
                                                         query,
                                                         start_sel="<span style='background-color: cyan'>",
                                                         stop_sel="</span>"))
        result = result.annotate(bodyline=SearchHeadline("description",
                                                         query,
                                                         start_sel="<span style='background-color: cyan'>",
                                                         stop_sel="</span>"))
        return result

    def filter(self, products):
        return self.q_search()


class OrderFilterStraregy(IProductFilterStrategy):
    def __init__(self, order_by):
        self.order_by = order_by

    def filter(self, products):
        return products.order_by(self.order_by)
