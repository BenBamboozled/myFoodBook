from django.urls import path
from conversations import views as convo_views

urlpatterns = [
    path('', convo_views.ConversationListView.as_view(), name='convos'),
    path('new/', convo_views.ConversationCreateView.as_view(), name='new-convo'),
    path('new/<str:username>', convo_views.ConversationCreateView.as_view(), name='new-user-convo'),
    path('<int:pk>/', convo_views.MessageFormView.as_view(), name='convo'),
    path('delete/<int:pk>/', convo_views.ConversationDeleteView.as_view(), name = 'delete-convo'),
]