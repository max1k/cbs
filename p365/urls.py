from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from p365.views import P365ListView, UploadFileView, P365DetailView, P365UnansweredListView, P365DateListView, P365OrgListView


urlpatterns = patterns('',
    url(r'^$', P365ListView.as_view(), name='p365-list'),
    url(r'^page(?P<page>\d+)/$', P365ListView.as_view(), name='p365-list-page'),
    url(r'^awaiting-response/$', P365UnansweredListView.as_view(), name='p365-unanswered'),
    url(r'^(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', P365DateListView.as_view(), name='p365-list-date'),

    url(r'^file(?P<pk>\d+)/$', P365DetailView.as_view(), name='p365-detail'),
    url(r'^new/$', UploadFileView.as_view(), name='p365-new'),
    url(r'^success-add/$', RedirectView.as_view(url='../'), name='p365-success-add'),
    url(r'^(?P<orgname>[\D -"]+)/$', P365OrgListView.as_view(), name='p365-orgmessage'),
    )