from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string, get_template
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from books.models import Book, Genres
from users.models import CustomUser, CustomUserProfile
from django.http import JsonResponse
import math
import json

import yaml
from urllib.request import urlopen
from bs4 import BeautifulSoup

DEFAULT_GENRES = ['fantasy', 'adventure', 'science fiction', 'dystopian', 'mystery', 'horror', 'thriller', 'romance']
def get_list_genre(all_genres, want_all=False):
    default_genres_present = set()
    formatted_genres = []

    for each_genre in all_genres:
        if (each_genre.title in DEFAULT_GENRES):
            default_genres_present.add(each_genre.title)
        formatted_genres.append({'title': each_genre.title, 'color': each_genre.color, 'type': each_genre.type})

    if (want_all):
        for each_genre in DEFAULT_GENRES:
            if (each_genre not in default_genres_present):
                genre = Genres.objects.get(title=each_genre)
                formatted_genres.append({'title': genre.title, 'color': genre.color, 'type': genre.type})

    return formatted_genres

def get_list_books(all_books):
    number_of_cols = 3
    formatted_books = []
    
    book_index = 0

    for eachBook in all_books:
        if (book_index%number_of_cols == 0):
            formatted_books.append([{"book": eachBook, "genres": eachBook.genres.all(),
                                "rating": eachBook.rating * [1] + (5-eachBook.rating) * [0]}])
        else:
            formatted_books[len(formatted_books)-1].append({"book": eachBook, "genres": eachBook.genres.all(), 
                                                "rating": eachBook.rating * [1] + (5-eachBook.rating) * [0]})
        book_index += 1

    if (len(formatted_books) > 0):
        while (len(formatted_books[len(formatted_books)-1]) != number_of_cols):
            formatted_books[len(formatted_books)-1].append(-1)

    return formatted_books

def index(request, filters=[]):
    if request.user.is_authenticated:
        users_books = Book.objects.filter(user=request.user)

        if filters != []:
            users_books = users_books.filter(genres=Genres.objects.get(title=filters))  

        users_genres = CustomUserProfile.objects.get(user=request.user).genres.all()

        all_used_genres = get_list_genre(users_genres)
        all_unique_genres = get_list_genre(users_genres, want_all=True)
        all_books = get_list_books(users_books)

        scraped_book_titles = request.session.pop('book_titles', [])

        context = {"books_and_genres": all_books, "all_used_genres": all_used_genres, 
                       "all_unique_genres": all_unique_genres, "suggestions": "why don't you work :()"}

        if (scraped_book_titles != []):
            context = {"books_and_genres": all_books, 
                       "all_used_genres": all_used_genres, 
                       "all_unique_genres": all_unique_genres, 
                       "suggestions": scraped_book_titles}
    
        return render(request, "add_book_popup.html", context=context) 
    
    return  HttpResponseRedirect('/books/user_login/')

def filter_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            filters = request.POST['bhelllo'].split(",")
            users_books = Book.objects.filter(user=request.user)

            for each_filter in filters:
                try:
                    users_books = users_books.filter(genres=Genres.objects.get(title=each_filter))
                except:
                    pass

            context = {"books_and_genres": get_list_books(users_books)}

            return render(request, "all_books_view.html", context=context) 
        
    return  HttpResponseRedirect('/books/user_login/')