from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden
from django.contrib import messages
from users.models import Notification, Follow
from .forms import PostForm
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Récupère les utilisateurs que l'utilisateur suit
            user_following = Follow.objects.filter(
                follower=self.request.user).values_list('following', flat=True)
            context['user_following'] = user_following
        else:
            context['user_following'] = []
        return context


@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Les invités ne peuvent pas voir les commentaires
        if (
            self.request.user.is_authenticated
                and self.request.user.username != 'guest'):
            context['comments'] = Comment.objects.filter(post=self.object)
        else:
            context['comments'] = None
        return context


@login_required
def add_comment_view(request, pk):
    # Vérifie si l'utilisateur est invité
    if request.user.username == 'guest':
        return HttpResponseForbidden(
            "Les invités ne sont pas autorisés à ajouter des commentaires.")

    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post=post, author=request.user, content=content)
        return redirect('posts:post_detail', pk=pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:post_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'posts/post_form.html'
    fields = ['image', 'caption']

    def get_success_url(self):
        return reverse_lazy('posts:post_detail', kwargs={'pk': self.object.pk})

    def test_func(self):
        # Seuls les auteurs peuvent modifier leur propre publication
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        # Seuls les auteurs peuvent supprimer leur propre publication
        post = self.get_object()
        return self.request.user == post.author


@login_required
def chat_room(request, room_name):
    return render(request, 'posts/chat_room.html', {'room_name': room_name})


@login_required
def inbox_view(request):
    received_messages = request.user.received_messages.all().order_by(
        '-timestamp')
    sent_messages = request.user.sent_messages.all().order_by('-timestamp')
    return render(request, 'users/inbox.html', {
        'received_messages': received_messages, 'sent_messages': sent_messages}
        )


@login_required
def post_create_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Notifier tous les abonnés de l'auteur
            followers = Follow.objects.filter(following=request.user)
            channel_layer = get_channel_layer()

            for follower in followers:
                # Enregistre la notification en base de données
                Notification.objects.create(
                    user=follower.follower,
                    post=post,
                    message=f"{request.user.username} a"
                    "ajouté une nouvelle publication."
                )
                # Envoie la notification via WebSocket
                async_to_sync(channel_layer.group_send)(
                    f"user_{follower.follower.id}",
                    {
                        'type': 'send_notification',
                        'message':
                        f"{request.user.username} a"
                        "ajouté une nouvelle publication."
                    }
                )
                Notification.objects.create(
                    user=follower.follower,
                    post=post,
                    message=f"{request.user.username} a"
                    "ajouté une nouvelle publication."
                )
                print(f"Notification créée pour {follower.follower.username}")
            messages.success(
                request, 'Votre publication a été ajoutée avec succès.')
            return redirect('posts:post_list')
    else:
        form = PostForm()
    return render(request, 'posts/post_form.html', {'form': form})


@login_required
@csrf_exempt  # Ajouter cette ligne si tu reçois des erreurs CSRF
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
            # Enlève le dislike si l'utilisateur a déjà disliké
            post.dislikes.remove(request.user)

        return JsonResponse({'total_likes': post.total_likes(),
                            'total_dislikes': post.total_dislikes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
@csrf_exempt  # Ajouter cette ligne si tu reçois des erreurs CSRF
def dislike_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)
            # Enlève le like si l'utilisateur a déjà liké²
            post.likes.remove(request.user)

        return JsonResponse({'total_likes': post.total_likes(),
                            'total_dislikes': post.total_dislikes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)
