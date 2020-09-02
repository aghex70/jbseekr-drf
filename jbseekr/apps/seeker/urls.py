from django.urls import path

from . import views

urlpatterns = [
    path('positions/generate/', views.PositionGeneratorViewSet.as_view({
        'post': 'create',
    }), name='generate'),
    path('positions/', views.PositionViewSet.as_view({
        'get': 'list',
    }), name='position_list'),
]
