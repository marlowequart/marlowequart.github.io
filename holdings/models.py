from django.db import models

# Create your models here.


# class Symbol(models.Model):
    # """Model representing a stock symbol."""
    # name = models.CharField(max_length=10, help_text='Enter a holding symbol (e.g. aapl)')
    
    # def __str__(self):
        # """String for representing the Model object."""
        # return self.name
		
		
#Used to generate URLs by reversing the URL patterns
from django.urls import reverse 

#Create models: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Models
class Holdings(models.Model):
	"""Model representing a holding (but not a specific holding)."""
	
	symbol = models.CharField(max_length=10, help_text='Enter a holding symbol (e.g. aapl)')
	name = models.CharField(max_length=20, help_text='Enter the company name')
	price = models.CharField(max_length=10, help_text='Enter the current price')
	shares = models.CharField(max_length=20, help_text='Enter the number of shares owned')
	
#    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)   
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file.
#    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')    
    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
#    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')
	
	def __str__(self):
		"""String for representing the Model object."""
		return self.symbol
	
	def get_absolute_url(self):
		"""Returns the url to access a detail record for this book."""
		return reverse('holding detail', args=[str(self.id)])