import os
import certifi
import logging


os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

logging.getLogger("SSL_Fix").info(f"SSL Certs forced to: {certifi.where()}")
