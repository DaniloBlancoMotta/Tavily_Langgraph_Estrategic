import os
import certifi
import logging

# Força o uso dos certificados válidos do pacote certifi
# Ignorando configurações de sistema quebradas (ex: PostgreSQL)
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

logging.getLogger("SSL_Fix").info(f"SSL Certs forced to: {certifi.where()}")
