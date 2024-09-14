from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie  # Import if you're using CSRF tokens
import openai
from django.contrib.auth.decorators import login_required

from django.contrib import auth
from django.contrib.auth.models import User
from.models import Chat

from django.utils import timezone

openai_api_key = ""
openai.api_key = openai_api_key

import openai
import time

def ask_openai(message):
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ]
    )
    
    answer = response.choices[0].message.content.strip()
    return answer


# Create your views here.

@login_required(login_url='login')  # Redirects to 'login' if not authenticated
def chatbot(request):
    # Now, request.user is guaranteed to be an authenticated user.

    chats = Chat.objects.filter(user=request.user)

    # Handle the POST request
    if request.method == 'POST':
        message = request.POST.get('message')

        # Basic error handling for missing 'message'
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        response = ask_openai(message)

        # You don't need to set created_at if you're using auto_now_add=True in your model.
        chat = Chat(user=request.user, message=message, response=response)
        chat.save()

        return JsonResponse({'message': message, 'response': response})

    # Handle non-POST requests
    return render(request, 'chatbot.html', {'chats': chats})


def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password = password)
        if user is not None:
            auth.login(request,user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid Usernaem or Passwrod'
            return render(request, 'login.html',{'error_message':error_message})
    else:    
        return render(request,'login.html')



def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username,email,password1)
                user.save()
                auth.login(request,user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html',{'error_message': error_message})
        else:
            error_message = 'Passwords dont match'
            return render(request, 'register.html',{'error_message': error_message})

    return render(request,'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')