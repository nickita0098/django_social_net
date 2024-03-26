from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Count
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView)

from .constants import POST_PER_PAGES
from .models import Post, Category, User
from .form import CommentForm, PostForm, UserForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin


def filter_post_for_public(manager):
    return manager.filter(pub_date__lte=now(),
                          is_published=True,
                          category__is_published=True)


def anotate_order_for_post(data):
    return data.select_related(
        'location', 'author', 'category'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class IndexListView(ListView):
    model = Post
    paginate_by = POST_PER_PAGES
    template_name = 'blog/index.html'
    queryset = anotate_order_for_post(filter_post_for_public(Post.objects))


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = POST_PER_PAGES
    category = None

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_queryset(self):
        return anotate_order_for_post(
            filter_post_for_public(
                Post.objects.filter(category=self.get_category())
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
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


class PostListView(ListView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    paginate_by = POST_PER_PAGES

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return get_object_or_404(filter_post_for_public(Post.objects),
                                 pk=self.kwargs['post_id'])

    def get_queryset(self):
        return self.get_object().comments.all().select_related('author')

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

    def dispatch(self, request, *args, **kwargs):
        self.post_for_comment = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_for_comment
        return super().form_valid(form)


class CommentDeletePost(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class ProfileListView(ListView):
    model = Post
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = POST_PER_PAGES

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        postset = self.get_object().posts.all()
        anotated_query = anotate_order_for_post(postset)
        if self.request.user == self.get_object():
            return anotated_query
        return filter_post_for_public(anotated_query)

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
