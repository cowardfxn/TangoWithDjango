from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from bing_search import run_query
from django.shortcuts import redirect
import os, json


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Category.objects.order_by('-views')[:5]

    context_dict = {'categories': category_list, 'pages': page_list}
    # return render(request, 'rango/index.html', context_dict)

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visit cookie.
    # If the cookie exists, we default to zero and cast that.
    # visits = int(request.COOKIES.get('visits', 1))
    visits = request.session.get('visits', 1)

    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).seconds > 0:
            # ... reassign the value of the cookie to +1 of what it was before...
            visits += 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    return render(request, 'rango/index.html', context_dict)

    # response = render(request, 'rango/index.html', context_dict)
    # # Does the cookie last_visit exist?
    # if 'last_visit' in request.COOKIES:
    #     # Yes it does, get the cookie value
    #     last_visit = request.COOKIES.get('last_visit')
    #     # Cast the value to a Python data/time object
    #     last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    #
    #     # If it's been more than a day since the last visit
    #     if (datetime.now() - last_visit_time).days > 0:
    #         visits += 1
    #         # ...and flag that the cookie last visit needs to be updated
    #         reset_last_visit_time = True
    # else:
    #     # Cookie last_visit doesn't exist, so flat that it should be set.
    #     reset_last_visit_time = True
    #
    #     context_dict['visits'] = visits
    #
    #     # Obtain our response object early so we can add cookie information.
    #     response = render(request, 'rango/index.html', context_dict)
    # if reset_last_visit_time:
    #     response.set_cookie('last_visit', datetime.now())
    #     response.set_cookie('visits', visits)
    #
    # # Return response back to the user, updating any cookies that need changed.
    # return response


def about(request):
    # return HttpResponse("Rango says here is the about page.<br/><a href='/rango'>Rango</a>")
    visits = request.session.get('visits', 1);
    last_visit = request.session.get('last_visit', str(datetime.now()))
    context_dict = {
        'visits': visits,
        'last_visit': last_visit
    }
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    # Create a context dictionary which can pass to the template rendering engine.
    context_dict = {}
    result_list = []
    try:
        # Can we find a category name slug with the given name?
        # If we can't the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict["category_name"] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under new pages.
        context_dict['pages'] = pages
        # We also add the context objects from the database to the context dictionary.
        # We'll use this in the template to varify that the category exists.
        context_dict["category"] = category
        context_dict["category_name_slug"] = category_name_slug

        # Search Context
        if request.method == 'POST':
            query = request.POST['query'].strip()

            if query:
                # Run our bing function to get the reuslt list
                context_dict["result_list"] = run_query(query.decode('gb2312'))

    except Category.DoesNotExist:
        # We get there if we didn't find the specific category
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    # A HTTP POST?
    if request.method == "POST":
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view
            # The user will be shown the homepage
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter the details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # render the form with error message (if any).
    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.isValid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # Probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes it to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we are interested in processing form data.
    if request.method == "POST":
        # Attempt to grap information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user project.
            user.set_password(user.password)
            user.save()

            # Now sort out the UseProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we are ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picutre = request.FILES['picture']

            # Now we save the UserProfile instance.
            profile.save()

            # Upate our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problem to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,
                  'rango/register.html',
                  {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
                  )


def user_login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == "POST":
        # Gather the username and password passed by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
        # because the request.POST.get returns None, if the value does not exist,
        # while the request.POST['<variable>'] will raise keyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django machinery to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a user object, the details are valid.
        # If None (Python's way of representing the absence of a value), no user
        # with matching confidentals was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled!")
        else:
            # Bad login details are provided, so we can't log the user in!
            print "Invalid user details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variable to pass to the template system, hence the
        # blank dictionary object.
        return render(request, 'rango/login.html', {})


@login_required
def restricted(request):
    render_cont = {"restrictedmessage": "Since you're loged in, you can see this text."}
    return render(request, 'rango/restricted.html', render_cont)


@login_required
def user_logout(request):
    # Since we know the user is now logged in, you can now just log them out.
    logout(request)

    # Take the user back to the home page
    return HttpResponseRedirect('/rango/')


def search(request):
    result_list = []
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our bing function to get the reuslt list
            result_list = run_query(query.decode('gb2312'))

    return render(request, 'rango/0search.html', {'result_list': result_list})


def track_url(request, page_id):
    # if request.method == 'GET':
    #     if 'page_id' in request.GET:
    #         page_id = request.GET['page_id']
    # Or
    # page_id = request.GET.get('page_id')

    page = Page.objects.get(id=page_id)
    if page:
        page.views += 1
        page.save()
        return redirect(page.url)
    else:
        return index(request)


@login_required
def like_category(request):
    cat_id = None
    if request.method == "GET":
        cat_id = request.GET.get("category_id")

    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()

    return HttpResponse(likes)


def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

    if max_results > 0:
        cat_list = cat_list[:max_results]

    return cat_list


@login_required
def suggest_category(request):
    result = []
    if request.method == "GET":
        starts_with = request.GET.get("suggestion")
        suggestions = get_category_list(5, starts_with)
        result = ", ".join([e.name for e in suggestions])

    return HttpResponse(result)


@login_required
def auto_add_page(request):
    context_dict = {}
    if request.method == "GET":
        page_url = request.GET.get("url")
        page_name = request.GET.get("name")
        category_id = request.GET.get("catid")

        try:
            category = Category.objects.get(id=category_id)
            Page.objects.get_or_create(category=category, title=page_name, url=page_url)

            pages = Page.objects.filter(category=category).order_by('-views')
            print pages
            context_dict['pages'] = pages
        except Exception, e:
            print e.message

    return HttpResponse()
    # return render(request, 'rango/page_list.html', context_dict)