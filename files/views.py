from django.shortcuts import render
from files.models import File
from files.serializers import FileSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from files.models import File

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    
    def create(self, request):
        file = super().create(request)
        file_url = file.data['file_url'].replace("/files/files","")
        if "https" in file_url:
            pass
        else:
            file_url = file_url.replace("http","https")
        File.objects.get(id=file.data['id']).delete()
        return Response(file_url)

class FileObjectViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    
    def create(self, request):
        file = super().create(request)
        file_url = file.data['file_url'].replace("/files/files","")
        if "https" in file_url:
            pass
        else:
            file_url = file_url.replace("http","https")
        File.objects.get(id=file.data['id']).delete()
        return Response({"url":file_url})
