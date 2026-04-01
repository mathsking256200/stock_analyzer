from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('analyze/', views.analyze_stock, name='analyze_stock'),
    path('stock/<slug:slug>/', views.stock_detail, name='stock_detail'),
    path('register/', views.register, name='register'),
    path("payment-success/", views.payment_success, name="payment_success"),
    path('login/', views.login_view, name='login'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('welcome/', views.welcome, name='welcome'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset/<str:token>/', views.email_reset, name='email_reset'),
    path("export-excel/", views.export_excel, name="export_excel"),
    path("send-watchlist-email/", views.send_watchlist_email, name="send_watchlist_email"),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
]
