#!/usr/bin/python
import sqlite3
import sys

# Check if the right number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python check_ip.py <IP>")
    sys.exit(1)

# Get the IP address from the command line
ip_to_check = sys.argv[1]

# Connect to SQLite database
conn = sqlite3.connect('/var/lib/f2b_auto_ignore/login_success.db')
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

