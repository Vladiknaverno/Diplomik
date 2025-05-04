from django.urls import path, include
from . import views
from .views import add_recipe
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('add/', add_recipe, name='add_recipe'),
    path('all_recipes/', views.all_recipes, name='all_recipes'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/saved/', views.saved_recipes, name='saved_recipes'),
    path('activity-log/', views.activity_log, name='activity_log'),
    path('recipe/edit/<int:pk>/', views.edit_recipe, name='edit_recipe'),
    path('recipe/delete/<int:pk>/', views.delete_recipe, name='delete_recipe'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('categories/', views.all_categories, name='all_categories'),
    path('category/<slug:slug>/', views.category_view, name='category_detail'),
    path('search_categories/', views.search_categories, name='search_categories'),
    path('profile/change-password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/change_password.html',
        success_url='/profile/'
    ), name='change_password'),
    path('recipes/<int:pk>/like/', views.like_recipe, name='like_recipe'),
    path('recipe/<int:pk>/save/', views.save_recipe, name='save_recipe'),
    path('recipe/<int:pk>/unsave/', views.unsave_recipe, name='unsave_recipe'),
    path('recipes/<int:pk>/add_comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('recipe/<int:pk>/rate/', views.rate_recipe, name='rate_recipe'),
]