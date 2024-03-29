from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from .constants import MAX_CHAR_LENGTH, MAX_TITLE_LEN, DEF_SUFFIX


User = get_user_model()


class CreatedAt(models.Model):
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        abstract = True


class IsPublishedCreatedAtModel(CreatedAt):
    is_published = models.BooleanField('Опубликовано', default=True,
                                       help_text='Снимите галочку, '
                                       'чтобы скрыть публикацию.')

    class Meta(CreatedAt.Meta):
        abstract = True


class Location(IsPublishedCreatedAtModel):
    name = models.CharField('Название места', max_length=MAX_CHAR_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return f'{self.name[:MAX_TITLE_LEN]:.<{DEF_SUFFIX}}'


class Category(IsPublishedCreatedAtModel):
    title = models.CharField('Заголовок', max_length=MAX_CHAR_LENGTH)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор', unique=True,
                            help_text='Идентификатор страницы '
                            'для URL; разрешены символы латиницы, '
                            'цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.title[:MAX_TITLE_LEN]:.<{DEF_SUFFIX}}'


class Post(IsPublishedCreatedAtModel):
    title = models.CharField('Заголовок', max_length=MAX_CHAR_LENGTH)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата и время публикации',
                                    help_text='Если установить дату и время '
                                    'в будущем — можно делать отложенные '
                                    'публикации.')
    image = models.ImageField('Фото', upload_to='post_images',
                              null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория')

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})

    def __str__(self):
        return f'{self.title[:MAX_TITLE_LEN]:.<{DEF_SUFFIX}}'


class Comment(CreatedAt):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             verbose_name='коментарий')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='автор')

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.pk})

    class Meta:
        verbose_name = 'коментации'
        verbose_name_plural = 'Коментарии'
        default_related_name = 'comments'

    def __str__(self):
        return f'{self.text[:MAX_TITLE_LEN]:.<{DEF_SUFFIX}}'
