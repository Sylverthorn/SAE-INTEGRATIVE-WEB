from django.db import models
from datetime import datetime
# Create your models here.


class Capteur(models.Model):
    id_capteur = models.CharField(max_length=50, default=None, primary_key=True)
    nom_capteur = models.CharField(max_length=100, default=None) 
    pieces = models.CharField(max_length=100, default=None) 
    maison = models.CharField(max_length=100, default=None)

    def __str__(self):
        return f"{self.nom_capteur} " 

    def dico(self):
        return {"id_capteur":self.id_capteur,"nom_capteur":self.nom_capteur, "pieces":self.pieces}
    

class Donnée(models.Model):
    id_capteur = models.ForeignKey("Capteur", default=None, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(default=datetime.now, null=True, blank=True)
    temperature = models.CharField(max_length=100)
    

    def __str__(self):
        return f"{self.id_capteur} " 

    def dico(self):
        return {"capteur":self.id_capteur, "timestamp":self.timestamp, "temperature":self.temperature}
    