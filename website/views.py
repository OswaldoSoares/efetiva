from django.shortcuts import render

def index_website(request):
    return render(request, 'website/index.html')