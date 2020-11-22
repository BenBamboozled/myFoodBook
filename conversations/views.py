from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.edit import ModelFormMixin, BaseCreateView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count

from .models import Message, Conversation
from .forms import ConversationCreateForm, MessageCreateForm

# Create your views here.
class ConversationCreateView(LoginRequiredMixin, CreateView):
    model = Conversation
    form_class = ConversationCreateForm

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        if self.kwargs.get('username'):
            initial['participants'] = User.objects.filter(Q(username=self.kwargs.get('username')) | Q(username=self.request.user.username)).all()
            exact = Conversation.objects.filter(participants__in=initial['participants'])
            if(exact):
                print(exact)
        return initial

    # def form_valid(self, form):
    #     # exact = Conversation.objects.annotate(count=Count('participants')).filter(count=len(form.instance.participants))
    #     # for partic in form.instance.participants:
    #     #     exact = exact.filter(participant=partic)
    #     # exact = exact.filter(count=len(form.instance.participants))
    #     convos = Conversation.objects.all()
    #     for convo in convos:
    #         if set([x.username for x in convo.participants.all()]) == set([x.username for x in form.instance.participants.all()]):
    #             exact = convo
    #     if(exact):
    #         # HttpResponseRedirect(reverse('{}'.format(exact.filter().first().pk)))
    #         print(exact)
    #     return super(CreateView, self).form_valid(form)

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