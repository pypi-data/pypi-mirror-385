from django.urls import path

from aldryn_search.views import AldrynSearchView


urlpatterns = [
    path('', AldrynSearchView.as_view(), name='aldryn-search'),
]
