from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Profile, Relationship, Comment
from django.contrib.auth.models import User
from taggit.models import Tag
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from . forms import AddPostForm,UserRegistrationForm,ProfileUpdateForm,AddCommentForm
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

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

##Class based view for creating a post
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['body','image','tags']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
            return reverse('my-profile')

##EditProfile fuinction provides form to allow user to update profile, will validate and update form if valid
@login_required
def editProfile(request):
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES,instance=request.user.profile)

        if p_form.is_valid:
           p_form.save()
           messages.success(request, f'Profile succesfully updated.')
           return redirect('my-profile')
    else:
        p_form=ProfileUpdateForm(instance=request.user.profile)

    context = {
        'p_form': p_form
    }

    return render(request,'foodBookApp/edit-profile.html', {'p_form': p_form})



#splash page for when users are not logged in
def splash(request):
    return render(request, 'foodBookApp/splash-page.html')

#home function checks if user is logged in and sends them to correct page
def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/profile')

    else:
        return HttpResponseRedirect('/splash')


#Generic class view that querys and shows all posts from logged in user
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name ='foodBookApp/profile.html' #<app>/</model>_<viewtype>.html
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-datePosted')

#generic class based view/form that allows user to update body and tags to a post, validates that the post belongs to user and will  update
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body', 'tags']

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

#generic class based view that allows user to delete post belonging to them after completing prompt
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url='/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False

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

#profile function based view that takes in username and allows another user to view that profile
def profile(request, username):
    viewer = Profile.objects.get(user=request.user)
    user = User.objects.get(username=username)
    if not user:
        return redirect('my-profile')
    
    profile = Profile.objects.get(user=user)
    posts = Post.objects.filter(user=user)

    context={
        'viewer': viewer,
        'username': username,
        'user': user,
        'profile': profile,
        'posts': posts
    }

    return render(request, 'foodBookApp/user-profile.html', context)

class ProfileListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'foodBookApp/profile-list.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs = Profile.objects.get_all_profiles(self.request.user)
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

def friends(request):
    profile = Profile.objects.get(user=request.user)
    context = {'profile':profile}
    return render(request,'foodBookApp/friends.html',context)




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

        rel = Relationship.objects.create(sender=sender, receiver=receiver, status='send')

        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('my-profile')

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
    return redirect('my-invites')

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
    profile = Profile.objects.get(user=request.user) 

    qs = profile.friends.all()
   
    results = [] 
    for friend in qs:
        posts = Post.objects.filter(user=friend.id)
        for post in posts:
            results.append(post)

    results.reverse()

    is_empty = False
    if len(results) == 0:
        is_empty = True

    context = {
            'posts': results,
            'is_empty': is_empty,
        }

    return render(request, 'foodBookApp/main-feed.html', context)

## function for when a user likes a post currrently just reload page
@login_required
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

    return JsonResponse(data, safe=False)









