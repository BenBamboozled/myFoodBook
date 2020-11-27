from django.test import TestCase
from django.contrib.auth.models import User

from foodBookApp.models import Post, Profile, Relationship, Comment

# Create your tests here. 

class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="user1", email="email@...", password="test_password")
        User.objects.create_user(username="user2", email="email@...", password="test_password")
        User.objects.create_user(username="user3", email="email@...", password="test_password")

        Post.objects.create(user=User.objects.get(pk=1))
        Post.objects.create(user=User.objects.get(pk=2))

    def test_tags(self):
        user1Post = Post.objects.get(pk=1)
        # test tags add and count
        user1Post.tags.add("a", "b", "c")
        self.assertEqual(user1Post.tags.all().count(), 3)
        
        # test tags filtering
        self.assertTrue(user1Post.tags.filter(name="b"))
        self.assertFalse(user1Post.tags.filter(name="d"))
        
        # test tags removing
        user1Post.tags.remove("b")
        self.assertFalse(user1Post.tags.filter(name="b"))
        self.assertEqual(user1Post.tags.all().count(), 2)


    def test_privacy_verbose(self):
        user1Post = Post.objects.get(pk=1)
        # test default public and display
        self.assertEqual(user1Post.privacy, 'public')
        self.assertEqual(user1Post.get_privacy_display(), 'Public')

        # test assign privacy and display
        user1Post.privacy = 'friends'
        self.assertEqual(user1Post.privacy, 'friends')
        self.assertEqual(user1Post.get_privacy_display(), 'Friends Only')

    def test_total_likes(self):
        # test total_likes() after each of various like add and remove
        user1Post = Post.objects.get(pk=1)
        self.assertEqual(user1Post.total_likes(), 0)

        user1Post.likes.add(User.objects.get(pk=1))
        self.assertEqual(user1Post.total_likes(), 1)

        user1Post.likes.add(User.objects.get(pk=1))
        self.assertEqual(user1Post.total_likes(), 1)

        user1Post.likes.add(User.objects.get(pk=2))
        self.assertEqual(user1Post.total_likes(), 2)

        user1Post.likes.add(User.objects.get(pk=3))
        self.assertEqual(user1Post.total_likes(), 3)

        user1Post.likes.remove(User.objects.get(pk=3))
        self.assertEqual(user1Post.total_likes(), 2)

class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username="test_user1", email="email@...", password="test_password")
        User.objects.create_user(username="test_user2", email="email@...", password="test_password")
        User.objects.create_user(username="test_user3", email="email@...", password="test_password")

    def test_privacy_verbose(self):
        # test privacy default, assign, and display
        user1Profile = Profile.objects.get(pk=1)

        self.assertEqual(user1Profile.privacy, 'public')
        self.assertEqual(user1Profile.get_privacy_display(), 'Public')

        user1Profile.privacy = 'friends'
        self.assertEqual(user1Profile.privacy, 'friends')
        self.assertEqual(user1Profile.get_privacy_display(), 'Friends Only')

    def test_get_friends_qs_and_total(self):
        # test get_friends() for queryset and total_friends() for count
        user1Profile = Profile.objects.get(pk=1)

        self.assertFalse(user1Profile.get_friends())
        self.assertEqual(user1Profile.total_friends(), 0)

        user1Profile.friends.add(User.objects.get(pk=2))
        self.assertTrue(user1Profile.get_friends())
        self.assertEqual(user1Profile.total_friends(), 1)

        user1Profile.friends.add(User.objects.get(pk=3))
        self.assertEqual(user1Profile.total_friends(), 2)
        
        # TODO: test and prevent profile from friending itself, or otherwise
        

    def test_can_view_privacy_permissions(self):
        # test can_view(request.user) for bool if meets privacy requirements
        user1Profile = Profile.objects.get(pk=1)

        self.assertTrue(user1Profile.privacy, 'public')
        user2 = User.objects.get(pk=2)

        self.assertTrue(user1Profile.can_view(user2))

        user1Profile.privacy = 'friends'
        self.assertFalse(user1Profile.can_view(user2))

        user1Profile.friends.add(User.objects.get(pk=2))
        self.assertTrue(user1Profile.can_view(user2))

        user1Profile.privacy = 'private'
        self.assertFalse(user1Profile.can_view(user2))

    # TODO: test save() override function

    def test_get_abs_url(self):
        # test if proper url is returned by reverse(name)
        user1Profile = Profile.objects.get(pk=1)
        self.assertURLEqual(user1Profile.get_absolute_url(), '/profile/{}/'.format(user1Profile.user.username))

# TODO: set and test relationship restrictions