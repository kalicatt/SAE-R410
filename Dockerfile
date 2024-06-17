# Utilisation de l'image de base nats
FROM nats:latest

# Copie du fichier de configuration local dans le conteneur
COPY nats-server.conf /nats-server.conf

# Commande à exécuter lorsque le conteneur démarre
CMD ["nats-server", "-c", "/nats-server.conf"]
