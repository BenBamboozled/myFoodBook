from django.db import models
from django.contrib.auth.models import User #for auth
from PIL import Image #For uploading images
from django.utils import timezone #for datePosted field in post model
from taggit.managers import TaggableManager #tags fors post
from django.db.models.signals import post_save #signal to creat profile
from django.shortcuts import render, redirect, reverse #for rendering htttp pages
from django.db.models import Q, Max #for complex queries on database

PRIVACY_CHOICES = (
    ('public', 'Public'),
    ('private', 'Private'),
    ('friends', 'Friends Only')
)
##Post Model holds all info for each user post, foreign key is user who poster
class Post(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    body = models.TextField(max_length=300)
    image = models.ImageField(blank=True, upload_to="post_pics")
    datePosted = models.DateTimeField(default=timezone.now)
    tags = TaggableManager(blank=True)
    likes = models.ManyToManyField(User, related_name='like_post')
    privacy = models.CharField(max_length=7, choices=PRIVACY_CHOICES, default='public')

    ordering = ['-datePosted']

    def total_likes(self):
        return self.likes.all().count()

#represent a comment to a post, hold the body of the comment, the post, and the user who posted the comment
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    body = models.TextField(max_length=300)
    datePosted =  models.DateTimeField(default=timezone.now)

##Profile MAnager povides additonal functions thatg interact with profile model
class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile= Profile.objects.get(user=sender)
        qs = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        print(qs)

        accepted = []
        for rel in qs:
            if rel.status == 'accepted':
                accepted.append(rel.receiver)
                accepted.append(rel.sender)
        print(accepted)

        available = [profile for profile in profiles if profile not in accepted]
        print("available")

        return available

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles



##Profile Model to hold details for user profile, User is one to one as each user has only one profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,blank=False)
    profilePic = models.ImageField(default="default.jpg", upload_to="profile_pics") 
    bio = models.TextField(max_length=200, blank=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    privacy = models.CharField(max_length=7, choices=PRIVACY_CHOICES, default='public')

    objects = ProfileManager()


    def get_friends(self):
        return self.friends.all()
    
    def total_friends(self):
        return self.friends.all().count()

    def can_view(self, user):
        return self.privacy == "public" or user == self.user or (user.is_authenticated and self.privacy == "friends" and Profile.objects.filter(friends=user).exists())

    def __str__(self): #to string for Profile Model
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):  #overrides save function to save image if any
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('user-profile', kwargs={'username': self.user.username})

STATUS_CHOICES = (
    (
        ('send', 'send'),
        ('accepted', 'accepted')
    )
)
#relationship manager provides a invataions receiver function for each user
class RelationshipManager(models.Manager):
    def invatations_received(self, receiver):
        qs = Relationship.objects.filter(receiver=receiver, status='send')
        return qs

##Relationship represents friend relation between two user, one user is sender of the friend request the other the receiver the two user become friends when the relationship is set to accepted
class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(max_length=8,choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = RelationshipManager()

    def __str__(self): #to string for Relationship Model
        return f'{self.sender.user.username} friend request {self.receiver.user.username}'



