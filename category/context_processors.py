from category.models import Category

def menu_links(request):
    return {"links": Category.objects.all()}
