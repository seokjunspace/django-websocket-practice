from django.shortcuts import render


def index(request):
    return render(request, 'tweet/index.html')


def room(request, room_name):
    return render(request, 'tweet/room.html', {
        'room_name': room_name
    })