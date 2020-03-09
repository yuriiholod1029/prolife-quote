from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin.sites import site
from django.urls import include, path

from prolife.core.views import sales

urlpatterns = [
    path('admin/', site.urls),
    path('', include('django.contrib.auth.urls')),
    path('core/report/sales/', sales, name='sales')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

site.index_title = ""
site.site_header = "Prolife Admin"
site.site_title = "Profile"