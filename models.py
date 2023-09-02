import os
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.core.files import File
from django.urls import reverse
from django.contrib.auth.models import User
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor.fields import RichTextField
from django.utils import timezone

from celery import shared_task
from datetime import timedelta
from haystack import signals


def create_slug(title):
    return slugify(title)

def book_image_path(instance, filename):
    book_name = instance.title
    book_name = book_name.replace(' ', '_')
    book_name = clean_filename(book_name)
    path = f'catalog/image/{book_name}/'
    return os.path.join(path, filename)


def book_directory_path(instance, filename):
    local_cleaned_filename = clean_filename(filename)
    return f'books/{instance.slug}/{local_cleaned_filename}'

def chapter_directory_path(instance, filename):
    local_cleaned_filename = clean_filename(filename)
    return f'books/{instance.book.slug}/{local_cleaned_filename}'


def clean_filename(filename):
    invalid_chars = {'/', '\\', '?', '%', '*', ':', '|', '"', '<', '>', '.'}
    for c in invalid_chars:
        filename = filename.replace(c, '')
    return filename




class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:tag_detail', args=[str(self.pk)])


class Fandom(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:fandom_detail', args=[str(self.pk)])


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:country_detail', args=[str(self.pk)])


class Genres(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:genres_detail', args=[str(self.pk)])







def get_reergard_user():
    return User.objects.get(username='Reergard')




class Chapter(models.Model):
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='book_chapters')
    title = models.CharField(max_length=255)
    content = RichTextField(blank=True, null=True)
    file = models.FileField(upload_to=chapter_directory_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(blank=False, null=False)
    price = models.DecimalField(max_digits=7, decimal_places=2, default=0.00)  # Цена главы
    purchased_by = models.ManyToManyField(User, blank=True, related_name="purchased_chapters")
    content_length = models.PositiveIntegerField(default=0)




    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        if self.file:
            chapter_file_path = os.path.join(settings.MEDIA_ROOT, 'books', self.book.slug, self.file.name)
            with open(chapter_file_path, 'wb') as f:
                for chunk in self.file.chunks():
                    f.write(chunk)













class Book(models.Model):

  ...
  
    user = models.ForeignKey(User, on_delete=models.SET(get_reergard_user), related_name='books')
    title = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag)
    genres = models.ManyToManyField(Genres)
    fandoms = models.ManyToManyField(Fandom)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to=book_directory_path, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    viewed_by = models.ManyToManyField(User, blank=True, related_name="viewed_books")  # Связь "многие ко многим" с моделью User, позволяет отслеживать, кто из пользователей просмотрел книгу.
    pub_date = models.DateField(verbose_name='Дата створення', default=timezone.now) # Дата створення
    last_updated = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='books/', blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=TRANSLATING)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            num = 2
            while Book.objects.filter(slug=self.slug).exists():
                self.slug = "{}-{}".format(slugify(self.title), num)
                num += 1

        if not self.image:
            no_image_path = os.path.join(settings.STATICFILES_DIRS[0], 'catalog/image/no_image.png')
            self.image.save('no_image.png', File(open(no_image_path, 'rb')))



        if self.pk:
            previous_image = Book.objects.get(pk=self.pk).image
            if self.image != previous_image:
                if previous_image:
                    previous_image_path = os.path.join(settings.MEDIA_ROOT, str(previous_image))
                    if os.path.exists(previous_image_path):
                        os.remove(previous_image_path)




    def avg_rating(self):
        avg = self.book_ratings.all().aggregate(Avg('stars'))
        return round(avg.get('stars__avg') or 0, 2)








class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

...
