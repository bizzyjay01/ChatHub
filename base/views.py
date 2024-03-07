from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib .auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib.auth import authenticate, login, logout, get_user_model
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.utils.safestring import mark_safe

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .tokens import account_activation_token

# Create your views here.

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    
    else:
        messages.error(request, "Activation link is invalid")

    return redirect('login')


def activateEmail(request, user, to_email):
    mail_subject = "[ChatHub]: Activate your user account."
    message = render_to_string('base/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[to_email])

    if email.send():
        messages.success(request, mark_safe(f'<h2>Dear <strong>{user.name}</strong>, please go to your email <strong>{to_email}</strong> inbox and click on received activation link to confirm and complete the registration. <strong>Note:</strong> Check your spam folder.</h2>'))
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

def index(request):
    return render(request, 'base/index.html')


def home(request):
    # q = request.GET.get('q') if request.GET.get('q') != None else "" 

    # OR
    if request.GET.get('q') != None:
        q=request.GET.get('q')
    else:
        q = ''
    # the variable name 'q' can be given any name
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q) | Q(host__username__icontains=q)) #icontains makes sure that whatever value we have in topic__name contains what's in request.GET.get(q). i.e you can enter q=jav in browser tab, and it will direct you to javascript room.
    # Now we can search by 4 different values

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))#[0:5] #i.e to only see messages in recent activities related to the room name being clicked
    # room_messages = Message.objects.all().order_by('-created')
    
    # Paginate the list of rooms
    paginator = Paginator(rooms, 10)  # Show 10 rooms per page
    page = request.GET.get('page', 1)
    
    try:
        rooms = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        rooms = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        rooms = paginator.page(paginator.num_pages)


    context = {'rooms':rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room=i
    room = Room.objects.get(id=pk) #get a specific room
    # room_messages = room.message_set.all() # to get all child objects of the model 'Message' for this particular room
    room_messages = room.message_set.all().order_by('-created') # to get all child objects of the model 'Message' for this particular room
    participants = room.participants.all()

    # comment/message in a room
    if request.method == 'POST':
        message = Message.objects.create( #from Message in models.py
            user = request.user,
            room = room, 
            body=request.POST.get('body') #i.e the body is going to be what we passed in the form (we get it).'body' is the name used in the room.html
        )
        room.participants.add(request.user) #i.e add participant when they comment
       
        return redirect('room', pk=room.id)

        
        

    context = {'room': room, 'room_messages':room_messages, 'participants':participants}
        
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete this message because you are not the owner")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})


 # before you can create room, user has to be logged in. so login_url = 'login' implies that if user is not logged in, redirect to login page
@login_required(login_url='login')
def createRoom(request):
    page = 'createroom'
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) # i.e let say we input 'python' this method is going to get the value of 'python' and return it inside the topic object. here created will be false because we already created python from our admin page. so if it can find it, it creates it
        
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),

        )
        # form = RoomForm(request.POST)
        # if form.is_valid:
        #     room = form.save(commit=False)
        #     room.host = request.user # i.e as the user creates the room, he becomes the host
        #     room.save()
        return redirect('home') # using the name value 'home' in urls.py, to redirect to homepage when the form is submitted
    context = {"form": form, "topics":topics, 'page':page}
    return render(request, 'base/room_form.html', context)

# TO Update the room
@login_required(login_url='login') # i.e only authentiated user can update a room
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) #i.e this form will be pre-filled with the particular 'room' value
    topics = Topic.objects.all()

    # i.e if user is not owner of the room
    if request.user != room.host:
        return HttpResponse("You are not allowed to update this room because you are not the owner")
 
    if request.method=='POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        # form = RoomForm(request.POST, instance=room) # u need to tell it which room to update
        # if form.is_valid:
        #     form.save()
        return redirect('home')


    context = {'form': form, "topics": topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("You are not allowed to delete this room because you are not the owner")
    
    if request.method=='POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':room})

def loginPage(request):
    page='login'

    if request.user.is_authenticated: # i.e a user should not go to a login page from browser tab when logged in.
        return redirect('home')

    if request.method=='POST': # If user input their information to login

        email=request.POST.get('email').lower()
        password=request.POST.get('password')

        # check if the user exist
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exist")
        
        # authenticate user. i.e to make sure whatever information provided to login is correct
        user = authenticate(request, email=email, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username OR password does not exist")
        
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    # if request.method=='POST':
        logout(request)
        return redirect('index')
    
    # return render(request,'base/logout.html')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        # In Django, the form.save(commit=False) method is used when you want to create or update a model instance based on the form data but delay saving it to the database immediately. This can be useful in scenarios where you need to perform additional processing or validation before saving the data to the database.
        if form.is_valid():
            user = form.save(commit=False) # delay saving it to the database immediately, in order to perform additional validation
            user.is_active=False # i.e if user doesn't have activated email. user.is_active will be false and he won't be able to login
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            # login(request, user)
            return redirect('login')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html', {'form':form})

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # get all this user rooms here in the profile
    rooms = user.room_set.all()
    room_messages = user.message_set.all() # messages sent by users in different room
    topics = Topic.objects.all()
    context = {'user': user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {"topics":topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages' : room_messages})
