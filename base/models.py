from django.db import models
from django.contrib.auth.models import AbstractUser

# # Create your models here.
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
     name = models.CharField(max_length = 200, null=True)
     email = models.EmailField(unique=True, null=True)
     bio = models.TextField(null=True)

     avatar = models.ImageField(null=True, default="avatar.svg") # the imagefield rely on a third party called 'pillow'. run python -m pip install pillow. it's an image processing library
     date_of_birth = models.DateField(null=True, blank=True)
     location = models.CharField(max_length=100, null=True, blank=True)

     USERNAME_FIELD = 'email'
     REQUIRED_FIELDS = []

     objects = CustomUserManager()

     def get_short_date_of_birth(self):
        """
        Returns the formatted date of birth as 'Month Day'.
        """
        if self.date_of_birth:
            return self.date_of_birth.strftime('%b %d')
        return None


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    #SET_NULL implies if a topic is deleted, keep the room, don't delete
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) # one to many. i.e a topic can be discussed in multiple rooms but a room can have only one topic
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #i.e null=True means the database can have this instance to be blank, blank to true also allows a form to be empty 
    
    # since User has already been connected with host, we need a related name
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) # takes a snapshot of time everytime we save or update. i.e to know when a room is updated
    created = models.DateTimeField(auto_now_add=True) # takes a snapshot of time when we first save this item. i.e to know when a room was created

    class Meta:
        # ordering = ['updated', 'created'] #ascending order
        
        ordering = ['-updated', '-created'] #descending order. i.e the recent room created will be at the top

    def __str__(self):
        return self.name
    

class Message(models.Model):
    # one to many relationship. i.e a user can have many messages in a room, whereas a message can have only one user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE) # CASCADE means when a room in model Room is deleted, all messages should be deleted in database
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created'] 

    def __str__(self):
        return self.body[0:50]

