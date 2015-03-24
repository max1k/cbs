from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from p311.views import P311ListView, P311DetailView, UploadFileView

urlpatterns = patterns('',
	url(r'^$', P311ListView.as_view(), name='p311-list'),
	url(r'^(?P<pk>\d+)/$', P311DetailView.as_view(), name='p311-detail'),
	url(r'^new/$', UploadFileView.as_view(), name='p311-new'),
	url(r'^success-add/$', RedirectView.as_view(url='../'), name='p311-success-add'),
	)