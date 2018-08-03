from django.conf.urls import url
from django.http import HttpResponse

from django.template import engines
from django.template.loader import render_to_string


DEBUG = True
SECRET_KEY = '410ngs3cr3tstr1ngw3lln0ts0l0ngw41tn0w1tsl0ng3n0ugh'
ROOT_URLCONF = __name__

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [
			'/Python/news_search/marketsearch/templates/'
		],
	},
]


def home(request):
	title= 'market search'

	html = render_to_string('home.html', {'title': title})
	
	return HttpResponse(html)
	
	
	
def about(request):
	title= 'market search'
	
	html = render_to_string('about.html', {'title': title})
	
	return HttpResponse(html)
	
	
urlpatterns = [
	url(r'^$', home, name='homepage'),
	url(r'^about/', about, name='aboutpage'),
]











#	django_engine = engines['django']
#	template = django_engine.from_string(home_template)
#	html = template.render({'title':title})