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

def get_list_genre(all_genres):
    formatted_genres = []
    for eachGenre in all_genres:
        formatted_genres.append({'title': eachGenre.title, 'color': eachGenre.color, 'type': eachGenre.type})
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

def index(request):
    if request.user.is_authenticated:            
        users_books = Book.objects.filter(user=request.user)
        users_genres = CustomUserProfile.objects.get(user=request.user).genres.all()

        all_genres = get_list_genre(users_genres)
        all_books = get_list_books(users_books)

        scraped_book_titles = request.session.pop('book_titles', [])

        context = {"books_and_genres": all_books, "all_unique_genres": all_genres, "suggestions": "why don't you work :()"}

        if (scraped_book_titles != []):
            context = {"books_and_genres": all_books, "all_unique_genres": all_genres, "suggestions": scraped_book_titles}
    
        return render(request, "add_book_popup.html", context=context) 
    
    return  HttpResponseRedirect('/books/user_login/')

def filter_view(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            print(request.POST.get(['bhelllo']))

        return index(request)
    
    return  HttpResponseRedirect('/books/user_login/')
    