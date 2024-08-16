from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_note, name='create_note'),
    path('notes/edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('add-tag/', views.add_tag, name='add_tag'),
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    path('check-reminders/', views.check_reminders, name='check_reminders'),
    path('filter-by-tag/<int:tag_id>/', views.filter_notes_by_tag, name='filter_notes_by_tag'),
    path('all-notes/', views.get_all_notes, name='get_all_notes'),
    path('filter-by-category/<int:category_id>/', views.filter_notes_by_category, name='filter_notes_by_category'),
    path('note-details/<int:note_id>/', views.get_note_details, name='get_note_details'),

]