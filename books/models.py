from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import uuid
from django.conf import settings

class Genres(models.Model):
    TYPE_CHOICES = [("C", "custom"),
                    ("D", "default")]
    title = models.CharField(max_length=50)
    user = models.ManyToManyField(settings.AUTH_USER_MODEL)
    color = models.CharField(max_length=7, default="#9ef9ff")
    type = models.CharField(choices=TYPE_CHOICES, default='C')

    def __str__(self):
        return "Title: " + self.title + ", Color: " + self.color + ", Type: " + self.type
    
# Create your models here.
class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, null=False)
    author = models.TextField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    genres = models.ManyToManyField(Genres, default=None)
    rating = models.IntegerField(default=5)
    cover = models.URLField(default="https://cdn.vectorstock.com/i/1000v/52/86/red-cartoon-question-mark-vector-51155286.jpg")

    def __str__(self):
        x= self.title + "     " + self.author + "    "
        for eachThink in self.genres.all():
            x += eachThink.__str__() + "   "
        return x
    
    def form_valid(self, form):
        form.instance.user = self.request.user # Fetch and assign the logged in user as user
        return super().form_valid(form)
    
        
    #to add a new Article object: python3 manage.py shell -> from articles.models import Articles ->
    #Articles.objects.all() -> a1 = Articles(title="..", content="..") -> a1.save() -> Articles.objects.all().values()