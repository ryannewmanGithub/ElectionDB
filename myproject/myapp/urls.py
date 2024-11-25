from django.urls import path
from .views import index, report

urlpatterns = [
    path('', index, name='index'),
    path('report/', report, name='report')
]
