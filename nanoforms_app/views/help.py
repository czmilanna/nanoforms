from django.shortcuts import render


def help(request):
    context = {
    }
    return render(request, 'help.html', context)
