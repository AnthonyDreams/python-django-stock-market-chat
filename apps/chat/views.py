from django.shortcuts import render
from .forms.UserForm import UserCreateForm
from .forms.RoomForm import RoomCreateForm
from django.views.generic import CreateView
from .models.ChatRoom import ChatRoom
from django.contrib.auth.decorators import login_required
# Create your views here.


class SignUpClassView(CreateView):
    form_class = UserCreateForm
    success_url = "/accounts/login"
    template_name = "registration/signup.html"

@login_required
def index(request):
    return render(request, 'chat/index.html',{"rooms": request.user.rooms.all()})

@login_required
def room(request, room_name):
    context = dict()
    chat_room = None

    try:
        chat_room = ChatRoom.objects.get(name=room_name.lower())
    except ChatRoom.DoesNotExist:
        chat_room = ChatRoom.objects.create(name=room_name.lower())
        chat_room.save()

    if chat_room:
        # TECHNICALL DOUBT I NEED TO GET THE LATEST 50 AND REVERSE IT TO ORDER BY FIRST AFTER THE SLICE[:50]
       context['messages'] = reversed(chat_room.messages.all().order_by("-created_at")[:50])
 
    try:
        chat_room.participants.get(id=request.user.id)
    except request.user.DoesNotExist:
        chat_room.participants.add(request.user)

    return render(request, 'chat/room.html', {
        'room_name': room_name,
        **context
    })