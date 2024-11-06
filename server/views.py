from django.shortcuts import render


def index(request):    ## pylint disable=no-member
    return render(request, "index.html",)
