from datetime import datetime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from rango.bing_search import run_query
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, ProfileForm, \
    UserRegistrationForm


def index(request):
    page_list = Page.objects.order_by('-views')[:5]
    category_list = get_category_list()
    context_dict = {'cat_list': category_list,
                    'categories': Category.objects.order_by('-likes')[:5],
                    'pages': page_list}

    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7],
                                               "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    return render(request, 'rango/index.html', context_dict)


def about(request):
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render(request, 'rango/about.html',
                  {'visits': count, 'cat_list': get_category_list()})


def suggest_category(request):
    starts_with = ''
    if request.method == 'GET' and 'suggestion' in request.GET:
        starts_with = request.GET['suggestion']

    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/category_list.html', {'cat_list': cat_list})


def category(request, category_slug):
    category_object = get_object_or_404(Category, slug=category_slug)

    pages = Page.objects.filter(category=category_object)

    context_dict = {'pages': pages, 'category': category_object,
                    'cat_list': get_category_list()}

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            context_dict['query'] = query
            result_list = run_query(query)
            for result in result_list:
                result['exists'] = False
                try:
                    Page.objects.get(url=result['link'])
                    result['exists'] = True
                except Page.DoesNotExist:
                    pass
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            category_object = form.save(commit=False)
            category_object.views = 0
            category_object.likes = 0
            category_object.save()

            return redirect('/rango/')
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render(request, 'rango/add_category.html',
                  {'form': form, 'cat_list': get_category_list()})


@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)


@login_required
@csrf_exempt
def add_page(request, category_slug):
    category_object = get_object_or_404(Category, slug=category_slug)

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)

            page.category = category_object
            page.views = 0

            page.save()

            if request.is_ajax():
                return HttpResponse(
                    json.dumps(
                        {'success': True,
                         'page': {
                             'id': page.id,
                             'title': page.title,
                             'url': page.url
                         }}
                    ),
                    content_type='application/json'
                )

            return redirect('rango.views.category', category_slug)
        else:
            print form.errors
            if request.is_ajax():
                return HttpResponse(
                    json.dumps(
                        {'success': False, 'errors': form.errors}
                    ),
                    content_type='application/json'
                )
    else:
        form = PageForm()

    return render(request, 'rango/add_page.html',
                  {'form': form, 'category': category_object,
                   'cat_list': get_category_list()})


def track_url(request):
    url = '/rango/'
    if request.method == 'GET' and 'page_id' in request.GET:
        page = get_object_or_404(Page, id=request.GET['page_id'])

        page.views += 1
        page.save()

        url = page.url

    return redirect(url)


def register(request):
    registered = False

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            if 'picture' in request.FILES:
                user.picture = request.FILES['picture']

            user.save()

            registered = True

        else:
            print form.errors

    else:
        form = UserRegistrationForm()

    return render(
        request,
        'rango/register.html',
        {'form': form, 'registered': registered,
         'cat_list': get_category_list()}
    )


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
        else:
            print form.errors

    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'rango/profile.html',
                  {'form': form, 'cat_list': get_category_list()})


def user_login(request):
    if request.user.is_authenticated():
        return redirect('/rango/')

    context_dict = {'cat_list': get_category_list()}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                if 'next' in request.GET:
                    return redirect(request.GET['next'])
                return redirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            context_dict['error'] = 'Invalid login details supplied.'
            context_dict['bad_details'] = True

    return render(request, 'rango/login.html', context_dict)


@login_required
def user_logout(request):
    logout(request)

    return redirect('/rango/')


def get_category_list(max_results=0, starts_with=''):
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        cat_list = cat_list[:max_results]

    return cat_list