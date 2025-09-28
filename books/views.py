from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic, View
from collections import defaultdict
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt,csrf_protect #Add this

from .models import Book, Genres
from users.models import CustomUser, CustomUserProfile

import yaml
from urllib.request import urlopen
from bs4 import BeautifulSoup 
import requests
import json

import os

#API KEY: AIzaSyC_JoRjMoFV7JdtBbZ5LA_LLfwZdv2QIEE
api_key_dir = os.path.dirname(__file__)
api_key_path = os.path.join(api_key_dir, 'api_key.txt')
API_KEY = open(api_key_path).read()

DEFAULT_COVER = "https://cdn.vectorstock.com/i/1000v/52/86/red-cartoon-question-mark-vector-51155286.jpg"

EDGE_CURL = "edge=curl"
ZOOM = "zoom="

DEFAULT_GENRES = ['fantasy', 'adventure', 'science fiction', 'dystopian', 'mystery', 'horror', 'thriller', 'romance']
COLORS = ["#ffafa9", "#ffbf91", "#fff7b3", "#d6ffaa", "#b1ffdc", "#aeb1ff", "#e6b7ff", "#ffdbf1"]

def increase_res(image_link):
    edge_curl_remove = image_link.find(EDGE_CURL)
    if (edge_curl_remove != -1):
        image_link = image_link[0:edge_curl_remove] + image_link[edge_curl_remove+len(EDGE_CURL):]
    zoom_increase = image_link.find(ZOOM)
    if (zoom_increase != -1):
        image_link = image_link[0: zoom_increase+len(ZOOM)-1] + "4" + image_link[zoom_increase+len(ZOOM)+1:0]

    return image_link

def scrapetheweb(input_text):
    book_titles_and_authors = []

    query = 'intitle:' + '+'.join(input_text.split(" "))
    url = "https://www.googleapis.com/books/v1/volumes?q="+query+"&maxResults=10"+"&key="+API_KEY
    response = requests.get(url)
    books_info = json.loads(response.content)
    
    i = 0

    for eachItem in books_info['items']:
        title, author, cover = "", "", "https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1673566495i/76703559.jpg"
        if ('title' in eachItem['volumeInfo'].keys()):
            title = eachItem['volumeInfo']['title']
        if ("authors" in eachItem['volumeInfo'].keys()):
            author = eachItem['volumeInfo']['authors']
        if ('imageLinks' in eachItem['volumeInfo'].keys()):
            cover = increase_res(eachItem['volumeInfo']['imageLinks']['smallThumbnail'])
            
        book_titles_and_authors.append({'book_title': title, 
                                        'book_author': ", ".join(author),
                                        'book_index': i, 
                                        'book_cover': cover})
        
        i += 1
    print(i)

    return book_titles_and_authors

def index(request):
    return render(request, 'maingbooks.html')

def get_suggested_books(request):
    suggested_book_titles = []
    if request.method == 'POST':
        book_title = request.POST['book_title']
        suggested_book_titles = scrapetheweb(book_title)

    return render(request, 'each_suggestion.html', {'suggested_book_titles': suggested_book_titles})

def whyNot(request):
    template='<html><body>why not </body></html>'
    return HttpResponse(content=template)

def add_user_genre():
    i = 0
    for eachGenre in DEFAULT_GENRES:    
        temp = Genres.objects.filter(title=eachGenre)
        if not temp.exists():
            g = Genres.objects.create(title=eachGenre, color=COLORS[i], type="D")
            g.save()
        i += 1
        print(i)

def create_account(request):
    add_user_genre()

    if request.user.is_authenticated:
        return redirect('index')
    if (request.method == 'GET'):
        return render(request, 'user_create.html')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            test = CustomUser.objects.get(username=username)
        except:
            user = CustomUser.objects.create_user(username=username, password=password)
            user_profile = CustomUserProfile.objects.create(user=user)

            return redirect('index')
        
        template='<html><body>gorl pretty sure you name an account </body></html>'
        return HttpResponse(content=template)

        
def login_request(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if (user is not None):
            login(request, user)
            # redirect('index')
            return redirect('index')
        else:
            return render(request, "user_login.html")
    else:
        return render(request, "user_login.html")
    
def logout_request(request):
    if request.user.is_authenticated:
        logout(request)
        template='<html><body>why not logout </body></html>'
        # return HttpResponseRedirect('/books/user_login/')
        return HttpResponse(content=template)
    else:
        template='you ain\'t even logged in girl'
        # return HttpResponse(content=template)
        return HttpResponseRedirect('/books/user_login/')
    
def add_throne(request):
    if request.user.is_authenticated:
        newBook = Book.objects.create(title='Throne of Glass', author='Sarah J. Maas', user=request.user)

        curr_genre = Genres.objects.filter(title='fantasy')
        if (curr_genre.exists()):
            newBook.genres.add(curr_genre[0])
        else:
            newGenre = Genres.objects.create(title='fantasy')
            newGenre.user.add(request.user)
            newBook.genres.add(newGenre)
            newGenre.save()
        newBook.save()

        print(Book.objects.all())
        print(len(list(Book.objects.all())))
        return redirect('index')
    else:
        return HttpResponseRedirect('/books/user_login/')
   

def add_book(request):
    if request.user.is_authenticated:
        if (request.method == 'POST'):
            book_title = request.POST['book_title']
            book_author = request.POST['book_author']
            book_cover = request.POST['book_cover']
            genres_selected = request.POST['genres_selected'].split(",")
            star_rating = request.POST['star_rating']

            newBook = Book.objects.create(title=book_title, author=book_author, user=request.user, rating=star_rating, cover=book_cover)
            user_profile = CustomUserProfile.objects.get(user=request.user)
            
            for eachGenre in genres_selected:
                curr_genre = Genres.objects.filter(title=eachGenre)
                if (curr_genre.exists()):
                    newBook.genres.add(curr_genre[0])
                    user_profile.genres.add(curr_genre[0])
                else:
                    newGenre = Genres.objects.create(title=eachGenre)
                    newGenre.user.add(request.user)
                    newBook.genres.add(newGenre)
                    newGenre.save()
                    user_profile.genres.add(newGenre)

            newBook.save()

            print(book_title)
            print(book_author)
            print(genres_selected)
            print(star_rating)
        return redirect('index')
    else:
        return HttpResponseRedirect('/books/user_login/')
    
    
# def delete_book(request):

    

# def add_book(request):
#     list = request.POST.get("list")

#     data = request.POST.get('my_data_field')
#     book_titles = scrapetheweb(data)
#     # Perform your desired operations with 'data'
#     result = f"Django function executed with: {data}"
#     print(result)
#     print("book_titles.    ", book_titles)
    
#     request.session['book_titles'] = book_titles
#     # return HttpResponseRedirect('/')
#     return render(request, "add_book_popup.html")



# def logout_request(request):
#     print("logout")
#     logout(request)
#     template='<html><body>why not </body></html>'
#     return HttpResponse(content=template)

# def login_request(request):
#     context={}
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['psw']
#         user = authenticate(username=username, password=password)
#         if (user is not None):
#             login(request, user)
#             return redirect('books:logout_request')
#         else:
#             return render(request, 'user_login')
#     else:
#         return render(request, 'user_login.html')