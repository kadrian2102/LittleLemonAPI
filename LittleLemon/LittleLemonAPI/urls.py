from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleItemView.as_view()),
    path('groups/manager/users', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerUserDetailView.as_view())
]