#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'WiFiTOUCH.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    #webhook
    url(r'^webhook/(?P<query_id>\w+)/$', 'AccessPoints.webhook.webhook'),
    url(r'^apiqueries/$', 'AccessPoints.views.apiqueries', name="apiqueries"),
    url(r'^$', 'AccessPoints.views.main', name="main"),
    url(r'^apiqueries/json/$', 'AccessPoints.views.apiqueries_json'),
    url(r'^apiqueries/action/$', 'AccessPoints.views.action_details'),
    url(r'^routers/$', 'AccessPoints.views.routers', name="routers"),
    url(r'^groups/$', 'AccessPoints.views.groups', name="groups"),
    url(r'^login/$', 'AccessPoints.views.login_view', name="login_view"),
    url(r'^router/details/json/$', 'AccessPoints.views.router_details_json'),
    url(r'^router/details/$', 'AccessPoints.views.show_router_details'),
    url(r'^router/details/apply/$', 'AccessPoints.views.router_details_apply'),
    url(r'^router/details/action/$', 'AccessPoints.views.show_router_details_by_action'),
    url(r'^groups/details/$', 'AccessPoints.views.group_details'),
    url(r'^groups/apply_profile/$', 'AccessPoints.views.group_apply_profile'),

    url(r'^network_profiles/$', 'AccessPoints.views.network_profiles', name="network_profiles"),
    #url(r'^/router/details/(?P<router_pk>\d+)/$', 'AccessPoints.views.router_details', name="router_details"),
    url(r'^logout/$', 'AccessPoints.views.logout_view', name='logout_view'),

    url(r'^debug/show/securityprofiles/(?P<router_pk>\d+)$', 'AccessPoints.views.showSecurityProfiles_debug'),
    url(r'^debug/show/wlans/(?P<router_pk>\d+)$', 'AccessPoints.views.showWLANs_debug'),


)
