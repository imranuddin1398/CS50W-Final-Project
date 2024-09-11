from django.urls import path
from store import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path("category/", views.category, name="category"),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("addReview/<int:id>", views.addReview, name="addReview"),
    path('complete_purchase/', views.complete_purchase, name='complete_purchase'),
    path('old-orders/', views.old_orders_view, name='old_orders'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)