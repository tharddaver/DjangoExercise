from django.conf.urls import patterns, url, include
from rango import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^category/', include([
        url(r'^add/$', views.add_category, name='add_category'),
        url(r'^like/$', views.like_category, name='like_category'),
        url(r'^suggest/$', views.suggest_category, name='suggest_category'),
        url(r'^(?P<category_slug>[-\w]+)/', include([
            url(r'^add-page/$', views.add_page, name='add_page'),
            url(r'^$', views.category, name='category')
        ]))
    ])),
    url(r'^about/', views.about, name='about'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^profile/$', views.profile_edit, name='profile'),
    url(r'^goto/$', views.track_url, name="track_url"),
)