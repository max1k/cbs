from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cbs.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^p311/', include('p311.urls')),
    url(r'^p365/', include('p365.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
