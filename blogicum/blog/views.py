from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Count
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView)

from .constants import POST_PER_PAGES
from .models import Post, Category, Comment, User
from .form import CommentForm, PostForm, UserForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin


def filter_post_for_public(manager):
    return manager.filter(pub_date__lte=now(),
                          is_published=True,
                          category__is_published=True)


def anotate_order_for_post(data):
    return data.select_related('location', 'author',
                               'category').annotate(
                                   comment_count=Count('comments'))


class IndexListView(ListView):
    model = Post
    ordering = 'pub_date'
    paginate_by = POST_PER_PAGES
    template_name = 'blog/index.html'
    queryset = anotate_order_for_post(filter_post_for_public(Post.objects))
    ordering = ('-pub_date')


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = POST_PER_PAGES
    ordering = ('-pub_date')
    category = None

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(Category,
                                          slug=self.kwargs['category_slug'],
                                          is_published=True)
        self.queryset = anotate_order_for_post(
            filter_post_for_public(
                Post.objects.filter(category=self.category)))
        # я не могу найти способ перенести строку,
        # чтобы автотесты это пропустили
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(ListView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    post = None
    paginate_by = 10

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(filter_post_for_public(Post.objects),
                                 pk=self.kwargs['post_id'])

    def get_queryset(self):
        self.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return Comment.objects.filter(post=self.post)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['post'] = self.get_object()
        return context


class PostDeletePost(PostMixin, DeleteView):

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])


class PostUpdateView(PostMixin, UpdateView):
    pass


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_for_comment
        return super().form_valid(form)


class CommentDeletePost(CommentMixin, OnlyAuthorMixin, DeleteView):

    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):

    template_name = 'blog/create.html'


class ProfileListView(ListView):
    model = Post
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = POST_PER_PAGES
    ordering = ('-pub_date')

    def get_object(self, queryset=None):
        username = self.kwargs['username']
        return get_object_or_404(User, username=username)

    def get_queryset(self):
        postset = self.get_object().posts.filter(author=self.get_object())
        if self.request.user == self.get_object():
            queryset = anotate_order_for_post(postset).order_by('-pub_date')
        else:
            queryset = anotate_order_for_post(
                filter_post_for_public(postset).order_by('-pub_date'))
        # я не могу найти способ перенести строку,
        # чтобы автотесты это пропустили
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])
