from django.urls import path
from .import views

from django.conf.urls.static import static
from django.conf import settings

app_name = 'books'

urlpatterns = [
    path(route='', view=views.index),
    # path(route='logout', view=views.logout_request, name='logout'),
    path(route='user_login/', view=views.login_request, name='login'),
    path(route='suggested_books/', view=views.get_suggested_books, name='suggested_books'),
    path(route='user_logout/', view=views.logout_request, name='logout'),
    path(route='whyNot/', view=views.whyNot, name='whyNot'),
    path(route='add_throne/', view=views.add_throne, name='add_throne'),
    path(route='add_book/', view=views.add_book, name='add_book'),
    path(route='create_account/', view=views.create_account, name='create_account')
]
