from django.shortcuts import render


def about(request):
    context = {
    }
    return render(request, 'about.html', context)
