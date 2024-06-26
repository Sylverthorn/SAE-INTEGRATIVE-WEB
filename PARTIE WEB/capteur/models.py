# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Capteur(models.Model):
    nom_capteur = models.CharField(max_length=100, blank=True, null=True)
    pieces = models.CharField(max_length=100, blank=True, null=True)
    emplacement = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'capteur'


class Donne(models.Model):
    capteur = models.ForeignKey(Capteur, models.DO_NOTHING, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    heure = models.CharField(max_length=50, blank=True, null=True)
    temperature = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donnÚe'
