from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser, Follow, Message, Notification
from django.http import JsonResponse
from django.contrib.auth import login
from posts.models import Post
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


# Vue pour s'inscrire
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre compte a été créé avec succès. '
                                      'Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# Vue pour la connexion en tant qu'invité
def guest_login_view(request):
    guest_user, created = CustomUser.objects.get_or_create(
        username='guest',
        defaults={
            'email': 'guest@example.com',
            'password': 'guestpassword'
        }
    )

    if created:
        guest_user.set_password('guestpassword')
        guest_user.save()

    login(request, guest_user)
    return redirect('posts:post_list')


# Vue de profil
@login_required
def profile_view(request, username):
    user_profile = get_object_or_404(CustomUser, username=username)
    posts = Post.objects.filter(author=user_profile)

    is_following = Follow.objects.filter(
        follower=request.user, following=user_profile
    ).exists()
    followers_count = Follow.objects.filter(following=user_profile).count()
    following_count = Follow.objects.filter(follower=user_profile).count()

    return render(request, 'users/profile.html', {
        'user_profile': user_profile,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts': posts
    })


# Vue pour suivre ou se désabonner (AJAX)
@login_required
@csrf_exempt
def follow_toggle_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        user_to_follow = get_object_or_404(CustomUser, username=username)

        if user_to_follow == request.user:
            return JsonResponse({
                'status': 'error',
                'message': 'Vous ne pouvez pas vous abonner à vous-même.'
            })

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=user_to_follow
        )

        if not created:
            follow.delete()
            following = False
        else:
            following = True

        followers_count = Follow.objects.filter(
            following=user_to_follow).count()

        return JsonResponse({
            'status': 'ok',
            'following': following,
            'followers_count': followers_count
        })

    return JsonResponse({'status': 'error', 'message': 'Requête non valide.'})


# Vue pour la boîte de réception
@login_required
def inbox_view(request):
    conversations = CustomUser.objects.filter(
        id__in=Message.objects.filter(recipient=request.user).values_list(
            'sender', flat=True
        )
    )
    return render(
        request, 'users/inbox.html', {'conversations': conversations})


# Vue pour discuter avec un utilisateur spécifique
@login_required
def chat_view(request, username):
    recipient = get_object_or_404(CustomUser, username=username)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) |
        Q(sender=recipient, recipient=request.user)
    ).order_by('timestamp')

    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(
                sender=request.user,
                recipient=recipient,
                content=message_content
            )
            return redirect('users:chat', username=recipient.username)

    return render(request, 'users/chat.html', {
        'recipient': recipient,
        'messages': messages
    })


# Vue pour les notifications
@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by(
        '-timestamp'
    )
    notifications.update(is_read=True)

    return render(request, 'users/notifications.html', {
        'notifications': notifications
    })
