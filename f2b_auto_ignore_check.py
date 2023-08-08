#!/usr/bin/python
import argparse
import configparser
import sqlite3
import os, sys


parser = argparse.ArgumentParser(description='Check if there were successful logins from an IP address')
parser.add_argument('-c', '--config', default='/etc/f2b_auto_ignore.conf',
                    help='Path to the configuration file')
parser.add_argument('-i', '--ip-address', required=True,
                    help='IP address to check for')
args = parser.parse_args()

config_file_path = args.config
ip_to_check = args.ip_address
config = configparser.ConfigParser()
config.read(config_file_path)

# Set default values
db_directory = "/var/lib/f2b_auto_ignore"
db_file = "login_success.db"
if 'Database' in config:
    db_directory = config['Database'].get('db_directory', db_directory)
    db_file = config['Database'].get('db_file', db_file)

db_path = os.path.join(db_directory, db_file)
# Check if the directory exists, and if not, create it
if not os.path.exists(db_directory):
    os.makedirs(db_directory, exist_ok=True)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if IP exists in the database
cursor.execute("SELECT * FROM logs WHERE ip = ?", (ip_to_check,))
result = cursor.fetchone()
conn.close()

if result:
    print(f"IP address {ip_to_check} exists in the database. Time logged: {result[0]}")
    sys.exit(0)  # Exit code 0 if IP is found
else:
    print(f"IP address {ip_to_check} does not exist in the database.")
    sys.exit(1)  # Exit code 1 if IP is not found

