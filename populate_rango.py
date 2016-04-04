__author__ = 'fanxn'
# _*_ encoding: utf-8 _*_

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testsite001.settings")

import django

django.setup()

from rango.models import Category, Page


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    return p


def add_cat(name):
    c = Category.objects.get_or_create(name=name)[0]
    return c


def update_cat(name, views, likes):
    c = Category.objects.filter(name=name).update(views=views, likes=likes)
    return c


def populate():
    python_cat = add_cat("Python")
    update_cat(name="Python",
               views=128,
               likes=64)
    add_page(cat=python_cat,
             title="Official Python Tutorial",
             url="http://docs.python.org/2/tutorial")

    add_page(cat=python_cat,
             title="How To Think Like a Computer Scientist",
             url="http://www.greedteapress.com/thinkpython")

    add_page(cat=python_cat,
             title="Learn Python in 10 Minutes",
             url="http://www.korokithakis.net/tutorials/python/")

    django_cat = add_cat("Django")
    update_cat(name="Django",
               views=64,
               likes=32)
    add_page(cat=django_cat,
             title="Official Django Tutorial",
             url="https://docs.djangoproject.com/en/1.8/intro/tutorial01/")

    add_page(cat=django_cat,
             title="Django Rocks",
             url="https://www.djangorocks.com/")

    add_page(cat=django_cat,
             title="How To Tango With Django",
             url="https://www.tangowithdjango.com/")

    frame_cat = add_cat("Other Frameworks")
    update_cat(name="Other Frameworks",
               views=32,
               likes=16)
    add_page(cat=frame_cat,
             title="Bottle",
             url="https://bottlepy.org/docs/dev/")

    add_page(cat=frame_cat,
             title="Flask",
             url="https://flask.procoo.org/")


    # Print out what we have added to the user.
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print "-{0}-{1}".format(str(c), str(p))


def populate2():
    search_cat = add_cat("Search Engine")
    add_page(search_cat, "Google", "http://www.google.com/")
    add_page(search_cat, "sov5", "http://www.sov5.com/")
    add_page(search_cat, "bing", "http://www.bing.com/")

    pic_cat = add_cat("Picture Engine")
    add_page(pic_cat, "bing", "http://cn.bing.com/images?FORM=Z9LH")
    add_page(pic_cat, "Baidu", "http://image.baidu.com/")

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print "-{0}-{1}".format(str(c), str(p))


def modifyPage(title):
    pages = Page.objects.filter(title=title)
    for page in pages:
        view = page.views + 1
        Page.objects.filter(title=title).update(views=view)

if __name__ == "__main__":
    print "Starting Rango population script..."
    # Delete all
    Category.objects.all().delete()
    Page.objects.all().delete()

    populate2()
    populate()
    for p in Page.objects.all():
        modifyPage(p.title)
        print "{0}.views = {1}".format(p.title, p.views)
