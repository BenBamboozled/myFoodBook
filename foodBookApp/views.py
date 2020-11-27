from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post, Profile, Relationship, Comment
from .forms import UpdatePostForm, UserRegistrationForm, ProfileUpdateForm, SearchForm, AddCommentForm, UserUpdateForm

from dal import autocomplete
from taggit.models import Tag
from itertools import chain # for merging querysets

##Register function provides registration form and validates form and saves once complete
def register(request):
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Account succesfully created.')
                return redirect('login')
        else:
            form = UserRegistrationForm()
        return render(request, 'foodBookApp/register.html', {'form': form})

#returns profiles and posts based of user search query
def search_results(request):
    query = request.GET.get('q')
    if not query:
        # print ("No query")
        return render(request, 'foodBookApp/search.html')

    # todo: user setting to hide profile from searches
    profiles = Profile.objects.filter(user__username__icontains=query).order_by('user__username')

    paginator = Paginator(profiles, 5)
    page = request.GET.get('pagea')
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        profiles = paginator.page(1)
    except EmptyPage:
        profiles = paginator.page(paginator.num_pages)

    # filter posts so that only public posts are always displayed and 
    # friends-only posts are displayed if requesting user is a friend of the post's user
    posts = Post.objects.filter(tags__name__icontains=query)
    
    if request.user.is_authenticated:
        posts = posts.filter(Q(privacy="public") | (Q(privacy="friends") & Q(user__profile__friends=request.user)))
    else:
        posts = posts.filter(privacy="public") 
    posts = posts.order_by('-datePosted')

    paginator = Paginator(posts, 5)
    page = request.GET.get('pageb')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'profiles': profiles,
        'posts': posts,
    }

    return render(request, 'foodBookApp/search.html', context)


#Taggit is used for tags in user posts
class TagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


#splash page for when users are not logged in
def splash(request):
    return render(request, 'foodBookApp/splash-page.html')

#home function sends user to main feed
def home(request):
    return HttpResponseRedirect(reverse('main-feed'))

#list all profiles that are public so other user  can interact with eachother
class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'foodBookApp/profile-list.html'
    context_object_name = 'qs'
    paginate_by = 10

    def get_queryset(self):
        qs = Profile.objects.exclude(privacy='private') #show all profiles except private ones
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        rel_r = Relationship.objects.filter(sender=profile)
        rel_s = Relationship.objects.filter(receiver=profile)
        rel_receiver = []
        rel_sender = []
        for item in rel_r:
            rel_receiver.append(item.receiver.user)
        for item in rel_s:
            rel_sender.append(item.sender.user)
        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True

        return context   

#Generic class view that querys and shows all posts from logged in user
class ProfilePagePostListView(ListView):
    model = Post
    template_name ='foodBookApp/user-profile.html' #<app>/</model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        # returns queryset of public posts; also friends-only posts if requester is friend
        profile = Profile.objects.get(user__username=self.kwargs.get('username'))
        qs = Post.objects.filter(user=profile.user)

        if self.request.user == profile.user: 
            qs.order_by('-datePosted') #if profile belongs to log in user returns all posts even private ones
            return qs

        if self.request.user.is_authenticated and profile.privacy == 'public': #if user is logged in and the current profile is public
            if self.request.user in profile.friends.all(): 
                qs = qs.filter(Q(privacy="public") | (Q(privacy="friends"))) #if friends show all public and friends only posts
            else:
                qs = qs.filter(privacy="public") #else jsut show public post
        else:
            if not self.request.user.is_authenticated: #if user is not logged in
                if profile.privacy == 'public':
                    qs = qs.filter(privacy="public") #show only public posts if profile privacy is public
                else:
                    qs = qs.exclude(user=profile.user) #else dont show any posts because user is not loggged in and the profile is either private or friends only
            else:
                if self.request.user in profile.friends.all():
                    qs = qs.filter(Q(privacy="public") | (Q(privacy="friends"))) #will show if profile is friends only
                else:
                    qs = qs.exclude(user=profile.user)

        qs.order_by('-datePosted')
        return qs

    def get_context_data(self, **kwargs):
        context = super(ProfilePagePostListView, self).get_context_data()

        rel_receiver = []
        rel_sender = []

        if self.request.user.is_authenticated:
            user = User.objects.get(username=self.request.user)
            profile = Profile.objects.get(user=user)
            rel_r = Relationship.objects.filter(sender=profile)
            rel_s = Relationship.objects.filter(receiver=profile)
            for item in rel_r:
                rel_receiver.append(item.receiver.user)
            for item in rel_s:
                rel_sender.append(item.sender.user)
        
        user = User.objects.get(username=self.kwargs.get('username'))
        profile = Profile.objects.get(user=user)
        can_view = profile.can_view(self.request.user)

        context["rel_receiver"] = rel_receiver
        context["rel_sender"] = rel_sender
        context['is_empty'] = False
        if len(self.get_queryset()) == 0:
            context['is_empty'] = True
        context['user'] = user
        context['can_view'] = can_view

        context['profile'] = profile
        return context

# generic class view to update a profile
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'foodBookApp/edit-profile.html'

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

# generic class view to update a post
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'foodBookApp/edit-user.html'
    success_url='/settings'

    def get_object(self):
        return self.request.user
        
##Class based view for creating a post
class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = UpdatePostForm
    model = Post

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user-profile', kwargs={'username':self.request.user.username})

#generic class based view/form that allows user to update body and tags to a post, validates that the post belongs to user and will  update
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    form_class = UpdatePostForm
    model = Post

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('user-profile', kwargs={'username':self.request.user.username})

#generic class based view that allows user to delete post belonging to them after completing prompt
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    # success_url='/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

    def get_success_url(self):
        return reverse('home')

#generic class based view for each post
class PostDetailView(DetailView):
    model = Post

def post(request, pk):
    post = Post.objects.get(id=pk)
    comments = Comment.objects.filter(post=post)
    total_comments = Comment.objects.filter(post=post).count()

    new_comment = None

    if request.method == 'POST':
        c_form = AddCommentForm(data=request.POST)

        if c_form.is_valid:
           new_comment = c_form.save(commit=False)
           new_comment.post = post
           new_comment.user = request.user
           new_comment.save()
           post.total_comments = Comment.objects.filter(post=post).count()
           post.save()
           messages.success(request, f'Comment added')
           return redirect(request.META.get('HTTP_REFERER'))
    else:
        c_form=AddCommentForm()


    context={
        'post': post,
        'comments': comments,
        'c_form': c_form,
        'total_comments': total_comments
    }

    return render(request, 'foodBookApp/post_detail.html', context)

## user profile view that shows all photosd based on their privacy level
def photos(request, username):
    user = User.objects.get(username=username)
    if not user:
        return redirect('user-profile', kwargs={'username':request.user.username})
    
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user)
    can_view = profile.can_view(request.user)
    rel_profile = Profile.objects.get(user=request.user)
    rel_r = Relationship.objects.filter(sender=rel_profile)
    rel_s = Relationship.objects.filter(receiver=rel_profile)
    rel_receiver = []
    rel_sender = []
    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    for item in rel_s:
        rel_sender.append(item.sender.user)
    context = {
        'username': username,
        # 'user': user,
        'profile': profile,
        'posts': posts,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'can_view':can_view
        }

    return render(request, 'foodBookApp/user-photos.html', context)

##returns a webpage with the logged in users photos
@login_required
def my_photos(request):
    profile = Profile.objects.get(user=request.user)

    posts = Post.objects.filter(user=request.user)

    context={
        'profile': profile,
        'posts': posts
    }

    return render(request, 'foodBookApp/my-photos.html', context)

 
## returns the friend of the current logged in user
@login_required
def friends(request):
    profile = Profile.objects.get(user=request.user)
    context = {'profile':profile}
    return render(request,'foodBookApp/my-friends.html',context)

#returns a users profile with there added friends list
def user_friends(request, username):    
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)
    can_view = profile.can_view(request.user)
    rel_profile = Profile.objects.get(user=request.user)
    rel_r = Relationship.objects.filter(sender=rel_profile)
    rel_s = Relationship.objects.filter(receiver=rel_profile)
    rel_receiver = []
    rel_sender = []
    for item in rel_r:
        rel_receiver.append(item.receiver.user)
    for item in rel_s:
        rel_sender.append(item.sender.user)

    context = {
        'profile':profile,
        'rel_receiver': rel_receiver,
        'rel_sender': rel_sender,
        'can_view':can_view
        }

    return render(request,'foodBookApp/user-friends.html',context)

#allow user to view invites
@login_required
def invites_view(request):
    profile = Profile.objects.get(user=request.user)
    qs = Relationship.objects.invatations_received(profile)
    results = list(map(lambda x: x.sender, qs))

    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
        'qs': results,
        'is_empty': is_empty,
    }

    return render(request, 'foodBookApp/my-invites.html', context)


#send a friend invite
@login_required
def send_invatation(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        rel = Relationship.objects.filter(sender=receiver, receiver=sender)
        if not rel:
            rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('user-profile', kwargs={'username':request.user.username})

##remove a specified user from the logged in users friends list
@login_required
def remove_from_friends(request):
    if request.method=='POST':
        pk = request.POST.get('profile_pk')
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)

        rel = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )
        rel.delete()
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('my-invites')

##to accept a friend invite
@login_required
def accept_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        if rel.status == 'send':
            rel.status = 'accepted'
            rel.save()
    return redirect(request.META.get('HTTP_REFERER'))

##to send a friend invite
@login_required
def reject_invatation(request):
    if request.method=="POST":
        pk = request.POST.get('profile_pk')
        receiver = Profile.objects.get(user=request.user)
        sender = Profile.objects.get(pk=pk)
        rel = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        rel.delete()
    return redirect('my-invites')

#returns basic home feed, queries freinds of a proile then gets all of there posts
def get_main_feed(request): 
    results = [] 
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user) 
        qs = profile.friends.all()
        
        for friend in qs:
            posts = Post.objects.filter(user=friend.id)
            for post in posts:
                results.append(post)

    for post in Post.objects.filter(privacy='public'):
            if post not in results and post.user.profile.privacy != 'private' :  
                results.append(post) # only add post if nota already in main feed

    results.reverse()

    context = {
        'posts': results,
    }

    return render(request, 'foodBookApp/main-feed.html', context)

## function for when a user likes a post
def like(request, pk):
    user = request.user
    profile = Profile.objects.get(user=user)
    post = Post.objects.get(id = pk)

    if(post):
        if user in post.likes.all():
            post.likes.remove(user)
            label = 'Like'
        else:
            post.likes.add(user)
            label = 'Unlike'

    
    data = {
        'likes': post.likes.all().count(),
        'label': label
    }

    if not request.user.is_authenticated:
        error = "Must be logged in"
        data = {
        'likes': post.likes.all().count(),
        'label': label,
        'error': error
        }
        return JsonResponse(data, safe=False)

    return JsonResponse(data, safe=False)

@login_required
def user_settings(request):
    return render(request, 'foodBookApp/user-settings.html')

# class UserSettingsView(LoginRequiredMixin, FormView):
#     template_name = 'foodBookApp/user-settings.html'

@login_required
def delete_profile(request):
    user = request.user
    user.delete()
    messages.success(request, 'Profile successfully deleted.')
    return redirect('home')

@login_required
def disable_profile(request):
    user = request.user
    user.is_active = False
    user.save()
    messages.success(request, 'Profile successfully disabled.')
    return redirect('home')
