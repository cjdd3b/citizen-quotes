from django.conf.urls import patterns, include, url
from tastypie.api import Api
from quotex.apps.content.views import IndexView
from quotex.apps.content.api import QuoteResource, SourceResource

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Register resources with Tastypie
v1_api = Api(api_name='v1')
v1_api.register(QuoteResource())
v1_api.register(SourceResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'quotex.views.home', name='home'),
    # url(r'^quotex/', include('quotex.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^api/', include(v1_api.urls), name="api"),
)
