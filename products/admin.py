from django.contrib import admin

from products.models import Categories, Products


# admin.site.register(Categories)
# admin.site.register(Products)


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ('name',)
    }


@admin.register(Products)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": ('name',)
    }
    list_display = ["name", "quantity", "price", "discount"]
    list_editable = ["quantity", "discount"]
    search_fields = ["name"]
    list_filter = ["discount", "quantity", "category", "price"]
    fields = [
        "name",
        "category",
        "quantity",
        "slug",
        "description",
        ("price", "discount"),
        "image",
    ]
