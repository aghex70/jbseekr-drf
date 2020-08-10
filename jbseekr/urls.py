"""jbseekr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os


from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

TITLE = "Mapfre API-SAM-{} API".format(os.getenv('PROJECT', 'MDH'))

admin.site.site_header = 'Servicio de Autorizaciones Médicas'
admin.site.index_title = 'Gestión de tareas periódicas'

swagger_info = openapi.Info(
    title=TITLE,
    default_version='v1',
    description="Mapfre API",
    terms_of_service="",
    contact=openapi.Contact(email="support@i2tic.com"),
    license=openapi.License(name=""),
)

SchemaView = get_schema_view(
    validators=['ssv', 'flex'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jbseekr.apps.seeker.urls')),
    url(r'^swagger(?P<format>.json|.yaml)$', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
