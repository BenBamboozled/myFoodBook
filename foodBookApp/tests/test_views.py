from django.test import RequestFactory, TestCase, tag
from django.contrib.auth.models import AnonymousUser, User
from django.urls import reverse

from foodBookApp.models import Post, Profile, Relationship, Comment
# function views
from foodBookApp.views import register, search_results, splash, home, post, photos, my_photos, friends, user_friends, invites_view, send_invatation, remove_from_friends, accept_invatation, reject_invatation, get_main_feed, like, user_settings, delete_profile, disable_profile
# class-based views
from foodBookApp.views import TagAutocomplete, ProfileListView, ProfilePagePostListView, ProfileUpdateView, UserUpdateView, PostCreateView, PostUpdateView, PostDeleteView

# TODO Important: tests for common user actions
# most pages should have fixed top navbar
# if authed: profile dropdown, post, messages, invites, friends, search options
#   profile dropdown: view profile, edit profile, settings, logout 
#       view:'/profile/<selfUsername>'; edit:'/profile-edit'; settings:'/settings'; '/logout'
#   post: '/post', new post form
#   messages: '/convos', list conversations
#   invites: '/my-invites', list friend requests
#   friends: '/friends', list friends
#   users: '/explore/users', list profiles(public only)
# else login/register button and search field options
#   pressing as anon login/register should lead to '/splash' 
#       login: ; register: 

# profile: '/profile/<username>', header with profilePic, names, button links
#   self: post, edit, friends, photos; all self posts feed
#   public: all can view friends, photos; authed can message, relationship
#   friends-only: only friends can message, view friends, photos; all can relationship
#   private: only self can see friends, photos; none can message; all can relationship

# posts: mainfeed, searchresults, profiles; create, detail, list, update
#   public posts always available
#   friends-only posts available if is_friends, can_view
#   private only available to poster

# '/' should lead to '/main' page with featured posts and main feed with public posts


# test auth for proper POST processing, redirects, template, and context
class AuthenticationTest(TestCase):
    def test_register(self):
        response = self.client.post(reverse('register'), {'username':'test_user1','email':'test_user1@email.com','password1':'a_super_duper_key', 'password2':'a_super_duper_key'})
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='test_user1'))
        self.assertFalse(response.context)

        response = self.client.post(reverse('register'), {'username':'bad','email':'bad','password1':'bad', 'password2':'a'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'foodBookApp/register.html')
        self.assertTrue(response.context.get('form'))
        self.assertFalse(User.objects.filter(username='bad'))

    def test_login(self):
        response = self.client.post(reverse('register'), {'username':'test_user1','email':'test_user1@email.com','password1':'a_super_duper_key', 'password2':'a_super_duper_key'})
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(self.client.login(username='test_user1', password='a_super_duper_key'))

    # TODO: auth views: change/reset pw


# test search_results for no query redirect, filter querysets(posts and profiles), paginator, context, redirects, and template
class SearchTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='test_user1', email='test_user1@...', password='test_password')
        User.objects.create_user(username='test_user2', email='test_user2@...', password='test_password')
        Post.objects.create(user=User.objects.get(pk=1))

    def search_success_results_context_count(self, query, context, count):
        response = self.client.get(reverse('search'), {'q':query})
        self.assertEqual(response.status_code, 200)
        contextObj = response.context['{}'.format(context)]
        self.assertEqual(len(contextObj.object_list), count)

    def test_blank_query_redirect(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_no_results(self):
        self.search_success_results_context_count('abc', 'profiles', 0)
        self.search_success_results_context_count('abc', 'posts', 0)

    def test_profile_search(self):
        user2 = User.objects.get(pk=2)
        profile2 = Profile.objects.get(user=user2)
        profile2.privacy = 'private'
        self.search_success_results_context_count('user2', 'profiles', 1)
        profile2.privacy = 'friends'
        self.search_success_results_context_count('user2', 'profiles', 1)
        self.search_success_results_context_count('test', 'profiles', 2)
        self.search_success_results_context_count('test', 'posts', 0)

    def test_profile_search_authed(self):
        self.client.force_login(User.objects.get(pk=1))
        self.test_profile_search()

    @tag('focus')
    def test_post_search_tag(self):
        self.search_success_results_context_count('abc', 'posts', 0)

        profile1 = Profile.objects.get(pk=1)
        profile2 = Profile.objects.get(pk=2)
        post1 = Post.objects.get(user=profile1.user)
        post1.tags.add('abc')
        self.assertTrue(post1.privacy == 'public')
        self.search_success_results_context_count('abc', 'posts', 1)

        post1.tags.remove('abc')
        self.search_success_results_context_count('abc', 'posts', 0)

    def test_post_search_anon(self):
        profile1 = Profile.objects.get(pk=1)
        profile2 = Profile.objects.get(pk=2)
        post1 = Post.objects.get(user=profile1.user)
        post1.tags.add('abc')

        self.assertTrue(post1.privacy == 'public')
        self.search_success_results_context_count('abc', 'posts', 1)

        post1.privacy = 'private'
        post1.save()
        self.assertTrue(post1.privacy == 'private')
        self.search_success_results_context_count('abc', 'posts', 0)

        post1.privacy = 'public'
        post1.save()
        self.assertTrue(post1.privacy == 'public')
        self.search_success_results_context_count('abc', 'posts', 1)

        post1.privacy = 'friends'
        post1.save()
        self.assertTrue(post1.privacy == 'friends')
        self.search_success_results_context_count('abc', 'posts', 0)
        profile1.friends.add(profile2.user)
        profile1.save()
        profile2.friends.add(profile1.user)
        profile2.save()
        self.search_success_results_context_count('abc', 'posts', 0)

    def test_post_search_authed(self):
        profile1 = Profile.objects.get(pk=1)
        profile2 = Profile.objects.get(pk=2)
        post1 = Post.objects.get(user=profile1.user)
        post1.tags.add('abc')
    
        self.client.force_login(profile2.user)
        self.assertTrue(post1.privacy == 'public')
        self.search_success_results_context_count('abc', 'posts', 1)

        post1.privacy = 'private'
        post1.save()
        self.assertTrue(post1.privacy == 'private')
        self.search_success_results_context_count('abc', 'posts', 0)

        post1.privacy = 'friends'
        post1.save()
        self.assertTrue(post1.privacy == 'friends')
        self.search_success_results_context_count('abc', 'posts', 0)
        profile1.friends.add(profile2.user)
        profile1.save()
        profile2.friends.add(profile1.user)
        profile2.save()
        self.search_success_results_context_count('abc', 'posts', 1)


class SimpleRenderRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='test_user1', email='test_user1@...', password='test_password')

    def test_home_redirect(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('main-feed'))

    def test_splash_render(self):
        template = 'foodBookApp/splash-page.html'
        response = self.client.get(reverse('splash-page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_user_settings(self):
        redirect_template = 'foodBookApp/login.html'
        template = 'foodBookApp/user-settings.html'
        response = self.client.get(reverse('user-settings'))
        self.assertRedirects(response, '/login/?next={}'.format(reverse('user-settings')))

        self.client.force_login(User.objects.get(pk=1))
        response = self.client.get(reverse('user-settings'))
        self.assertTemplateUsed(response, template)
        self.assertEqual(response.status_code, 200)

# TODO: test post classes create, update, detail, delete
#       test post functions: post for comments, likes for likes
#       TODO: test incorrent create/update/delete for user2 as user1
class PostViewsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='test_user1', email='test_user1@...', password='test_password')

    def test_post_create(self):
        user1 = User.objects.get(pk=1)
        self.assertFalse(Post.objects.all())

        response = self.client.post(reverse('new-post'), {'user':user1, 'body':'testbody'})
        self.assertRedirects(response, '/login/?next={}'.format(reverse('new-post')))

        self.client.force_login(user1)
        response = self.client.post(reverse('new-post'), {'user':user1, 'body':'testbody', 'privacy':'public'})
        # print(response.context_data.get('form').errors)
        self.assertRedirects(response, reverse('user-profile', kwargs={'username':user1.username}))
        self.assertEqual(Post.objects.all().count(), 1)
        self.assertTemplateUsed('foodBookApp/new-post.html')

    def test_post_update(self):
        user1 = User.objects.get(pk=1)
        self.assertFalse(Post.objects.all())
        Post.objects.create(user=user1, body='testbody', privacy='public')
        post1 = Post.objects.get(pk=1)
        self.assertEqual(post1.body, 'testbody')
        self.assertEqual(post1.privacy, 'public')

        response = self.client.post(reverse('edit-post', kwargs={'pk':1}), {'user':user1, 'body':'editedbody', 'privacy':'private'})
        self.assertRedirects(response, '/login/?next={}'.format(reverse('edit-post', kwargs={'pk':1})))

        self.client.force_login(user1)
        response = self.client.post(reverse('edit-post', kwargs={'pk':1}), {'user':user1, 'body':'editedbody', 'privacy':'private'})
        # print(response.context_data.get('form').errors)
        self.assertRedirects(response, reverse('user-profile', kwargs={'username':user1.username}))
        post1 = Post.objects.get(pk=1)
        self.assertEqual(post1.body, 'editedbody')
        self.assertEqual(post1.privacy, 'private')
        self.assertTemplateUsed('foodBookApp/post_form.html')
        post1 = Post.objects.get(pk=1)

    def test_post_delete(self):
        user1 = User.objects.get(pk=1)
        self.assertFalse(Post.objects.all())
        Post.objects.create(user=user1, body='testbody', privacy='public')
        self.assertTrue(Post.objects.all())
        
        response = self.client.post(reverse('delete-post', kwargs={'pk':1}))
        self.assertRedirects(response, '/login/?next={}'.format(reverse('delete-post', kwargs={'pk':1})))
        self.assertTrue(Post.objects.all())

        self.client.force_login(user1)
        response = self.client.post(reverse('delete-post', kwargs={'pk':1}), follow=True)
        print('redirected: {}'.format(response.get('location')))
        self.assertFalse(Post.objects.all())
        self.assertTemplateUsed('foodBookApp/post_confirm_delete.html')
        self.assertRedirects(response, reverse('main-feed'))

    def test_post_detail_comment(self):
        pass

    def test_post_like_unlike(self):
        pass

# TODO: test profile classes list, update, detail(and post list)
#       test self and others photos and friends

# TODO: test relationships: invites send/receive/accept/decline, add/remove friend

# TODO: test user update class, funcs: delete/disable profile