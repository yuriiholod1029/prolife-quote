from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.sites import site
from django.urls import include, path

urlpatterns = [
    path('admin/', site.urls),
    path('', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

site.index_title = ""
site.site_header = "Prolife Admin"
site.site_title = "Profile"