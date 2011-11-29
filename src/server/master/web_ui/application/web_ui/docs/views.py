from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from main.views.shared import is_admin, get_user, auth_required, admin_required
from forms import PageForm
from models import Page

def index(request):
    return HttpResponseRedirect('/docs/Documentation')

def view(request, name):
    """Shows a single wiki page."""
    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        page = Page(name=name)

    return render_to_response('wiki/view.html', {
        'page': page, 
        'admin': is_admin(request),
        'user': get_user(request),
        'navbar':Page.objects.get(name='NavBar'),
    })

@auth_required
@admin_required
def edit(request, name):
    """Allows users to edit wiki pages."""
    try:
        page = Page.objects.get(name=name)
    except Page.DoesNotExist:
        page = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if not page:
                page = Page()
            page.name = form.cleaned_data['name']
            page.content = form.cleaned_data['content']

            page.save()
            return HttpResponseRedirect('../../%s/' % page.name)
    else:
        if page:
            form = PageForm(initial=page.__dict__)
        else:
            form = PageForm(initial={'name': name})

    return render_to_response('wiki/edit.html', {
        'form': form, 
        'admin': is_admin(request),
        'user': get_user(request),
        'navbar':Page.objects.get(name='NavBar'),
    })
