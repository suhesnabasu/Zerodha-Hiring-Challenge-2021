from django.urls import path
from .views import home, sending_json_data
urlpatterns = [
    path('', home, name = 'home_page'),
    path('json_data/<str:q>',sending_json_data, name = 'sending_json_data'),
    path('json_data/',sending_json_data, name = 'sending_json_data_no_query'),
]
