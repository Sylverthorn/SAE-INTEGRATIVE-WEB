import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
import datetime
from datetime import datetime as dt
from cachetools import TTLCache 
import threading
import time

# Configuration des brokers et topics
brokers = ["test.mosquitto.org"]
topics = ["IUT/Colmar2024/SAE2.04/Maison1", "IUT/Colmar2024/SAE2.04/Maison2"]

# Configuration du cache avec TTL 
cache = TTLCache(maxsize=1000, ttl=300)  

# Configuration de la base de données
db_config = {
    'host': '192.168.74.135',
    'user': 'djangoUser',
    'password': 'toto',
    'database': 'test2'
}

# DdB
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['password'],
            database=db_config['database']
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def insert_capteur(connection, id_capteur, nom_capteur, pieces, maison):
    query = f"""
    INSERT INTO app_capteur_capteur (id_capteur, nom_capteur, pieces, maison)
    VALUES ('{id_capteur}', '{nom_capteur}', '{pieces}' , '{maison}');
    """
    execute_query(connection, query)

def insert_donnee(connection, id_capteur, timestamp, temperature):
    query = f"""
    INSERT INTO app_capteur_donnée (id_capteur_id, timestamp, temperature)
    VALUES ('{id_capteur}', '{timestamp}', '{temperature}');
    """
    print(f"Executing query: {query}")
    execute_query(connection, query)

# MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for topic in topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    Topic = msg.topic
    print(f"Topic: {Topic}\nMessage: {message}\n")
    process_message(message, Topic)

def process_message(message, topic):
    maison_part = topic.split('/')
    maison = maison_part[3]

    parts = message.split(',')
    id_capteur = parts[0].split('=')[1]
    nom_capteur = "Capteur_" + parts[0].split('=')[1]
    pieces = parts[1].split('=')[1]

    if len(parts) > 5 and parts[5]:
        temperature = parts[4].split('=')[1] + "," + parts[5]
    else:
        temperature = parts[4].split('=')[1]

    date = parts[2].split('=')[1]
    heure = parts[3].split('=')[1]
    timestamp = parts[2].split('=')[1] + ' ' + parts[3].split('=')[1]

    parsed_timestamp = datetime.datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
    formatted_timestamp = parsed_timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp = formatted_timestamp

    ignore_ids = ['Capteur1', '12A6B8AF6CD3', '12345']
    if id_capteur in ignore_ids:
        print(f"Capteur {id_capteur} ignoré. Ne sera pas inséré dans la base de données.")
    else:
        print(id_capteur, nom_capteur, pieces, date, heure, temperature)
        print('inserer dans le cache')
        cache_key = f"{id_capteur}_{timestamp}"
        cache[cache_key] = (id_capteur, nom_capteur, pieces, maison, timestamp, temperature)
        retry_cached_data()

def retry_cached_data():
    connection = create_connection()
    if connection is None:
        print("Impossible de se connecter à la base de données.")
        return
    for key in list(cache):
        id_capteur, nom_capteur, pieces, maison, timestamp, temperature = cache[key]
        try:
            insert_capteur(connection, id_capteur, nom_capteur, pieces, maison)
            insert_donnee(connection, id_capteur, timestamp, temperature)
            del cache[key]  # Supprimer du cache après insertion réussie
            print(f"Données insérées avec succès depuis le cache: {key}")
        except Error:
            print(f"Erreur lors de la réinsertion des données depuis le cache")
            break


clients = []

for broker in brokers:
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, 1883, 60)
    clients.append(client)

for client in clients:
    client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for client in clients:
        client.loop_stop()
        client.disconnect()
