
from .models import Category, Subcategory


def category_obj(request):
    category = Category.objects.all()
    subcategory = Subcategory.objects.all()
    return {
        'category': category,
        'subcategory': subcategory, }
