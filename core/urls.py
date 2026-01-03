from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('chat/', views.chat_page, name='chat'),
    path('profile/', views.profile, name='profile'),
    path('buy/', views.buy_tokens, name='buy'),
    # API endpoints
    path('api/chat/', views.api_chat, name='api_chat'),
    path('api/tokens/add/', views.api_add_tokens, name='api_add_tokens'),
    path('api/messages/', views.api_messages, name='api_messages'),
]
