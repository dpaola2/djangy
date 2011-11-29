from django.conf.urls.defaults import *

from templatetags.wiki import WIKI_WORD


urlpatterns = patterns('docs.views',
    (r'^$', 'index'),
    ('overview.html', 'index'),
    ('(?P<name>%s)/$' % WIKI_WORD, 'view'),
    ('(?P<name>%s)/edit/$' % WIKI_WORD, 'edit'),
)
