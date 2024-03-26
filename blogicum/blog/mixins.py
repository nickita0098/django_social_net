from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post, Comment
from .form import CommentForm, PostForm


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class PostMixin(OnlyAuthorMixin, LoginRequiredMixin):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    form_class = PostForm

    def handle_no_permission(self):
        return redirect(reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs[self.pk_url_kwarg]}
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = context['object']
        context['form'] = self.form_class(instance=instance)
        return context


class CommentMixin(LoginRequiredMixin):

    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})
