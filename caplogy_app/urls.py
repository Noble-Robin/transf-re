from django.urls import path
from . import views
from django.contrib.auth import logout
from django.shortcuts import redirect
from .views_school_image import school_image_upload
from .views_add_category import add_category_page

urlpatterns = [
    path('logout/', lambda r: (logout(r), redirect('login'))[1], name='logout'),
    path('login/',  views.login_view,   name='login'),
    path('logout/', lambda r: (logout(r), redirect('login'))[1], name='logout'),
    path('admin_page/',  views.admin_view,    name='admin_page'),
    path('users/promote/', views.promote_to_admin, name='promote_to_admin'),
    
    path('',        views.home_view,    name='home'),
    
    path('categories/', views.category_view, name='categories'),
    path('api/categories/', views.categories_api, name='categories_api'),
    path('categories/<int:category_id>/subcategories/', views.subcategory_view, name='subcategories'),
    path('categories/<int:category_id>/courses/', views.category_courses_view, name='category_courses'),
    path('categories/add/', views.add_category_view, name='add_category'),
    path('categories/delete/', views.delete_category_view, name='delete_category'),
    path('categories/add_page/', add_category_page, name='add_category_page'),
    
    path('courses/', views.courses, name='courses'),
    path('api/courses/', views.courses_api, name='courses_api'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/edit/<int:course_id>/', views.create_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('nc_dir/', views.list_nc_dir, name='list_nc_dir'),
    path('categories/<int:category_id>/school-image/', school_image_upload, name='school_image_upload'),
]
