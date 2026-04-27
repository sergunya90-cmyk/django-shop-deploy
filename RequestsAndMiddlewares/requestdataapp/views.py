from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse


def handle_file_upload(request):
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"]

        max_size = 1024 * 1024

        if myfile.size > max_size:
            return HttpResponse("Ошибка: Файл превышает допустимый размер в 1 МБ.", status=400)

        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        return HttpResponse(f"Файл '{filename}' успешно загружен!", status=200)

    return render(request, "requestdataapp/file-upload.html")