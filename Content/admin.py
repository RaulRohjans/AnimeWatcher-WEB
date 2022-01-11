from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category_class)
admin.site.register(Anime_class)
admin.site.register(Episode_class)
admin.site.register(SubmitAnime_class)
admin.site.register(MyList_class)