import logging
import os
from logging.handlers import RotatingFileHandler

log_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

if not os.path.exists(log_folder):
    os.makedirs(log_folder)


server_log = logging.getLogger("server_logs")
server_log.setLevel(logging.DEBUG)
server_log_handler = RotatingFileHandler(
    os.path.join(log_folder, "server_logs.log"), maxBytes=10000, backupCount=1
)
server_log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
server_log_handler.setFormatter(server_log_formatter)
server_log.addHandler(server_log_handler)

client_log = logging.getLogger("client_logs")
client_log.setLevel(logging.DEBUG)
client_log_handler = RotatingFileHandler(
    os.path.join(log_folder, "client_logs.log"), maxBytes=10000, backupCount=1
)
client_log_handler.setLevel(logging.DEBUG)
client_log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
client_log_handler.setFormatter(client_log_formatter)
client_log.addHandler(client_log_handler)
