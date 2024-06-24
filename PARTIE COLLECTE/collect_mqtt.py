import paho.mqtt.client as mqtt
import mysql.connector
from mysql.connector import Error
import datetime
import json
import os

# Configuration des brokers
brokers = ["test.mosquitto.org"]
topics = ["IUT/Colmar2024/SAE2.04/Maison1", "IUT/Colmar2024/SAE2.04/Maison2"]
cache_file = "cache.json"

# Database connection
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
        cache_query(query)

def cache_query(query):
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cache = json.load(file)
    else:
        cache = []
    
    cache.append(query)
    
    with open(cache_file, 'w') as file:
        json.dump(cache, file)

def execute_cached_queries(connection):
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            cache = json.load(file)
        
        for query in cache:
            execute_query(connection, query)
        
        os.remove(cache_file)

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

    maison_part = Topic.split('/')
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
        insert_capteur(connection, id_capteur, nom_capteur, pieces, maison)
        insert_donnee(connection, id_capteur, formatted_timestamp, temperature)

clients = []
connection = create_connection("192.168.74.135", "djangoUser", "toto", "test2")
execute_cached_queries(connection)

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
        pass
except KeyboardInterrupt:
    for client in clients:
        client.loop_stop()
        client.disconnect()
