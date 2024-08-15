from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_note, name='create_note'),
    path('notes/edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('filter-by-tag/<int:tag_id>/', views.filter_notes_by_tag, name='filter_notes_by_tag'),
    path('filter-by-category/<int:category_id>/', views.filter_notes_by_category, name='filter_notes_by_category'),
    path('add-tag/', views.add_tag, name='add_tag'),
]