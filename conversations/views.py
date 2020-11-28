from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.edit import ModelFormMixin, BaseCreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required

from .models import Message, Conversation
from .forms import ConversationCreateForm, MessageCreateForm

@login_required
def get_or_create_direct_conversation(request, username):
    users = [request.user, User.objects.get(username=username)]
    existing = Conversation.get_existing_convo(request, users)

    if not existing:
        convo = Conversation.objects.create()
        convo.participants.set(users)
        convo.save()
    else:
        convo = existing

    return HttpResponseRedirect(reverse('convo', kwargs={'pk':convo.pk}))

# Create your views here.
class ConversationCreateView(LoginRequiredMixin, CreateView):
    model = Conversation
    form_class = ConversationCreateForm

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        if self.kwargs.get('username'):
            initial['participants'] = User.objects.filter(Q(username=self.kwargs.get('username')) | Q(username=self.request.user.username)).all()
        else:
            initial['participants'] = self.request.user
        return initial

    # def get_form_kwargs(self):
    #     kwargs = super(ConversationCreateView, self).get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     # kwargs['q'] = self.request.GET.get('q')
    #     return kwargs

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    context_object_name = 'convos'
    template_name = 'conversations/conversations.html'
    paginate_by = 10

    def get_queryset(self):
        # qs = Message.objects.filter(conversation__participants=self.request.user).distinct('conversation')
        qs = Conversation.objects.filter(participants__in=[self.request.user]).all()
        # print('convos: {}'.format(qs))
        return qs

class ConversationDeleteView(LoginRequiredMixin, DeleteView):
    model = Conversation
    success_url = reverse_lazy('convos')

class MessageFormView(LoginRequiredMixin, BaseCreateView, ModelFormMixin, ListView):
    model = Message
    form_class = MessageCreateForm
    template_name = 'conversations/conversation.html'
    context_object_name = 'messages'
    success_url = ('#')
    paginate_by = 10

    def get_queryset(self):
        qs = Message.objects.filter(conversation=Conversation.objects.get(pk=self.kwargs.get('pk'))).order_by('-datetime')
        return qs

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        initial['sender'] = self.request.user
        initial['conversation'] = Conversation.objects.get(pk=self.kwargs.get('pk'))
        initial['receiver'] = initial['conversation'].participants.all()
        return initial

    def get_context_data(self, **kwargs):
        context = super(MessageFormView, self).get_context_data()
        # context['messages'] = Message.objects.filter(conversation=Conversation.objects.get(pk=self.kwargs.get('pk'))).order_by('-datetime')
        context['pk'] = self.kwargs.get('pk')
        # print ('messages: {}'.format(context['messages']))
        return context

    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super(MessageFormView, self).dispatch(request, *args, **kwargs)