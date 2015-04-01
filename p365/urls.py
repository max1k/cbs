from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from p365.views import P365ListView, UploadFileView


urlpatterns = patterns('',
    url(r'^$', P365ListView.as_view(), name='p365-list'),
    url(r'^page(?P<page>\d+)/$', P365ListView.as_view(), name='p311-list-page'),
    #url(r'^awaiting-response/$', P311UnansweredListView.as_view(), name='p311-unanswered'),
    #url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', P311DateListView.as_view(), name='p311-list-date'),

    #url(r'^file(?P<pk>\d+)/$', P311DetailView.as_view(), name='p311-detail'),
    url(r'^new/$', UploadFileView.as_view(), name='p365-new'),
    url(r'^success-add/$', RedirectView.as_view(url='../'), name='p365-success-add'),
    #url(r'^(?P<orgname>[\D -"]+)/$', P311OrgListView.as_view(), name='p311-orgmessage'),
    )