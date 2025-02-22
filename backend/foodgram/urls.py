from django.contrib import admin
from django.urls import include, path

from api.views import short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_link>/', short_link, name='short-link'),
]
