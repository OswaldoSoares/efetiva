""" MODÚLO CORE """
import mimetypes
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from website.models import FileUpload


@login_required(login_url="login")
def index_core(request):
    return render(request, "core/index.html")
