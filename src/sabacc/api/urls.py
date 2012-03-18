from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("api.views",
    url(r"^$", "index"),
    url(r"^logout$", "logout"),
)
