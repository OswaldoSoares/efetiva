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


@xframe_options_exempt
def visualizar_arquivo(request, id_file_upload):
    try:
        arquivo = FileUpload.objects.get(idFileUpload=id_file_upload)
        file_path = arquivo.uploadFile.path
        content_type, _ = mimetypes.guess_type(file_path)

        return FileResponse(open(file_path, "rb"), content_type=content_type)

    except Exception as error:
        raise Http404(f"Erro ao carregar arquivo: {error}")
