from django.urls import  path
from . import views

urlpatterns= [
    path('test/', views.testing_endpoint, name='test'),
    path('items/', views.items_list, name='items-list'),
    path('items/create/', views.post_item, name='post-item')
]