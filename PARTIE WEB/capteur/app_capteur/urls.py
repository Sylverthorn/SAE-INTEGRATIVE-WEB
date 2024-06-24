from django.urls import path
from . import views, views_donnee

urlpatterns = [
		path('', views.index),

        path('ajout/', views.ajout),
        path('traitement/', views.traitement),
        path('affiche/<int:id>/', views.affiche),
        path('update/<str:id_capteur>/', views.update),
        path('updatetraitement/<str:id_capteur>/', views.updatetraitement),
        path('delete/<str:id_capteur>/', views.delete),
        path('graph/<str:id_capteur>/', views.graph),


        path('donnee/', views_donnee.index),
        path('donnee/reset/', views.reset),
        path('donnee/export/', views_donnee.export_excel),
       ]