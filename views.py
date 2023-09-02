from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from .models import Book, Tag, Fandom, Country, Genres, Chapter, Comment, Like, Dislike, Rating
from .forms import BookForm, ChapterForm, CommentForm
from .forms import EditBookForm
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from users.models import Profile
import logging
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


...




@login_required
def rate_book(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        stars = request.POST.get('stars')
        book = get_object_or_404(Book, id=book_id)

        # Если пользователь уже оценивал эту книгу, обновите рейтинг
        rating, created = Rating.objects.get_or_create(user=request.user, book=book)
        rating.stars = stars
        rating.save()

        # Получить новый средний рейтинг
        avg_rating = book.avg_rating()

        # Ответите с новым средним рейтингом
        return JsonResponse({'avg_rating': avg_rating})
    else:
        return HttpResponseBadRequest("Invalid HTTP method")


...


