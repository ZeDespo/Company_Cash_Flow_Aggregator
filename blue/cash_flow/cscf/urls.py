from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_company, name='add_companies'),
    path('detailed/', views.detailed_company_view, name='detailed_company_view'),
    path('list/', views.list_all_companies, name='list_all_companies'),
    path('update/', views.update_company_data, name='update_companies')
]