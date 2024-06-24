from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .form import CapteurForm
from . import models
from .models import Capteur, Donnée
# Create your views here.

def index(request):
    liste_capteur = models.Capteur.objects.all()
    return render(request, 'Capteur/index.html', {"liste_capteur":liste_capteur,})

def affiche(request, id):
    Capteur = Capteur.objects.get(pk=id)
    return render(request,"Capteur/affiche.html", {"Capteur" : Capteur})






def ajout(request):
    if request.method == "POST":
        form = CapteurForm(request.POST)
        return render(request, "Capteur/ajout.html", {"form": form})
    else:
        form = CapteurForm()  
        return render(request, "Capteur/ajout.html", {"form": form})
    
def traitement(request):
    Capteur_form = CapteurForm(request.POST)
    if Capteur_form.is_valid():
        Capteur = Capteur_form.save()
        return HttpResponseRedirect("/ABS/Capteur/")
    else:
        return render(request, "Capteur/ajout.html", {"form": Capteur_form})







def update(request,id_capteur):
    Capteur = models.Capteur.objects.get(pk=id_capteur)
    form = CapteurForm(Capteur.dico())
    return render(request, "Capteur/ajout.html", {"form": form, "id_capteur": id_capteur})

def updatetraitement(request, id_capteur):
    capteur_instance = get_object_or_404(Capteur, id_capteur=id_capteur)
    if request.method == 'POST':
        form = CapteurForm(request.POST, instance=capteur_instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/")
    else:
        form = CapteurForm(instance=capteur_instance)
    return render(request, "Capteur/ajout.html", {"form": form, "id_capteur": id_capteur})



def delete(request, id_capteur):
    Capteur = models.Capteur.objects.get(pk=id_capteur)
    Capteur.delete()
    return HttpResponseRedirect("/")


import mysql.connector
def reset(request):
    

    mydb = mysql.connector.connect(
        user= 'djangoUser',
        password= 'toto',
        host= '192.168.74.135',
        database= 'test2'
        )
    mycursor = mydb.cursor()

    mycursor.execute("truncate table app_capteur_donnée")

    return HttpResponseRedirect("/donnee/")


import plotly.express as px
import pandas as pd


def graph(request, id_capteur):
    capteur = models.Capteur.objects.get(pk=id_capteur)

    try:
        capteur_data = Donnée.objects.filter(id_capteur_id=id_capteur).order_by('timestamp')
        capteur_df = pd.DataFrame(list(capteur_data.values('timestamp', 'temperature')))
        capteur_df['timestamp'] = pd.to_datetime(capteur_df['timestamp'])
        capteur_df['temperature'] = pd.to_numeric(capteur_df['temperature'])
        capteur_df = capteur_df.sort_values(by='timestamp')
        capteur_df['capteur'] = 'Capteur'
        
        fig = px.line(capteur_df, x='timestamp', y='temperature', title='Temperature en fonction du temps', markers=True)

       
        graph_html = fig.to_html(full_html=False)
        nondispo = ''
    except:
        nondispo = " AUCUNE DONNEES DISPONIBLE "
        graph_html = ''

    return render(request, 'Capteur/affiche.html', {'graph_html': graph_html, 'capteur': capteur , 'nondispo': nondispo})