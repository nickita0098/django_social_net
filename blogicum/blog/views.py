from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.shortcuts import redirect
from django.db.models import Count
from django.urls import reverse, reverse_lazy
from .models import Post, Category, Comments, User
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DeleteView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .constants import POST_PER_PAGES
from .form import CommentForm, PostForm, UserForm


def filter_post_for_public(manager):
    return (manager.select_related('location', 'author', 'category').
            filter(pub_date__lte=now(),
                   is_published=True,
                   category__is_published=True))


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class IndexListView(ListView):
    model = Post
    ordering = 'pub_date'
    paginate_by = POST_PER_PAGES
    template_name = 'blog/index.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return (filter_post_for_public(queryset)
                .order_by('-pub_date')
                .annotate(comment_count=Count('comments')))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy('blog:profile', args=[self.request.user.username])

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == obj.author:
            return obj
        else:
            return get_object_or_404(filter_post_for_public(Post.objects),
                                     pk=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context


class PostDeletePost(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    form_class = PostForm

    def handle_no_permission(self):
        return redirect(reverse('blog:post_detail',
                                kwargs={'post_id': self.kwargs['post_id']}))


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comments
    pk_url_kwarg = 'post_id'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_for_comment = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_for_comment
        return super().form_valid(form)


class CommentDeletePost(OnlyAuthorMixin, DeleteView):
    model = Comments
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comments
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/create.html'
    form_class = CommentForm
    success_url = reverse_lazy('blog:index')


class ProfileListView(ListView):
    model = Post
    slug_field = 'username'
    slug_url_kwarg = 'user_name'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        user_name = self.kwargs['user_name']
        user = get_object_or_404(User, username=user_name)
        if self.request.user == user:
            queryset = (Post.objects
                        .filter(author=user)
                        .order_by('-pub_date')
                        .annotate(comment_count=Count('comments')))
        else:
            queryset = (filter_post_for_public(Post.objects)
                        .filter(author=user)
                        .order_by('-pub_date')
                        .annotate(comment_count=Count('comments')))
        return queryset

    def get_context_data(self, **kwargs):
        user_name = self.kwargs['user_name']
        user = get_object_or_404(User, username=user_name)
        context = super().get_context_data(**kwargs)
        context['profile'] = user
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = POST_PER_PAGES

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
        queryset = (filter_post_for_public(category.posts)
                    .order_by('-pub_date')
                    .annotate(comment_count=Count('comments')))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
        context['category'] = category
        return context


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['form'] = UserForm(self.request.POST,
                                       instance=self.get_object())
        else:
            context['form'] = UserForm(instance=self.request.user)
        return context

    def test_func(self):
        return self.request.user.is_authenticated
