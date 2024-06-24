from django.shortcuts import render, HttpResponse
from .form import DonneeForm
from . import models
from .models import Donnée
# Create your views here.

from .form import DonneeFilterForm
import datetime

def index(request):
    form = DonneeFilterForm(request.GET)
    liste = Donnée.objects.all()
    js_enabled = request.GET.get('js', 'true') == 'true'

    if form.is_valid():
        maison = form.cleaned_data.get('maison')
        capteur = form.cleaned_data.get('capteur')
        pieces = form.cleaned_data.get('pieces')
        date_start = form.cleaned_data.get('date_start')
        date_end = form.cleaned_data.get('date_end')

        if maison:
            liste = liste.filter(id_capteur__maison__icontains=maison)
        if capteur:
            liste = liste.filter(id_capteur=capteur)
        if pieces:
            liste = liste.filter(id_capteur__pieces__icontains=(pieces))
        if date_start and date_end:
            liste = liste.filter(timestamp__range=(date_start, date_end))
        elif date_start:
            liste = liste.filter(timestamp__gte=date_start)
        elif date_end:
            liste = liste.filter(timestamp__lte=date_end)

    context = {
        'form': form,
        'liste_donnee': liste,
        'js_enabled': js_enabled,
    }
    return render(request, 'donnee/index.html', context)


import csv
def export_excel(request):
    data = Donnée.objects.all()
    response = HttpResponse(data , content_type='application/vnd.ms-excel;charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="books.xls"'

    writer = csv.writer(response)
    writer.writerow(['id_capteur', 'emplacement', 'timestamp', 'temperature'])
    for d in data:
        writer.writerow([d.id_capteur, d.id_capteur.pieces, d.timestamp, d.temperature])

    return response


