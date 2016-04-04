# _*_ coding: utf-8 _*_

from django.shortcuts import render
from django.http import HttpResponse

def first_page(request):
    return HttpResponse('西餐')

# Create your views here.
