#!/usr/bin/python
import argparse
import configparser
from daemonize import Daemonize
import io
import ipaddress
from collections import deque
import re
import subprocess
import sqlite3
import time
import os, sys
from datetime import datetime, timedelta


def read_args():
    global args

    parser = argparse.ArgumentParser(description='Monitor successful logins')
    parser.add_argument('-k', '--keep-minutes', type=int, default=120,
                        help='Minutes to keep the logs')
    parser.add_argument('-c', '--config', default='/etc/f2b_auto_ignore.conf',
                        help='Path to the configuration file')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help="Run as a daemon.")
    args = parser.parse_args()


def main():
    config_file_path = args.config
    config = configparser.ConfigParser()
    config.read(config_file_path)

    # Set default values
    minutes_to_keep = args.keep_minutes
    db_directory = "/var/lib/f2b_auto_ignore"
    db_file = "login_success.db"
    local_ips = ''
    local_ip_list = []

    def local_ips_to_ip_list(ip_string):
        """Get all IP addresses from IP in CIDR notation mask.

        Args:
            A string with on or multiple IPs in CIDR notation.

        Returns:
            A list of IP addresses in the subnet.
        """
        result = []
        cidr_ip_list = re.split(', ', local_ips)
        for cidr_ip in cidr_ip_list:
            network = ipaddress.ip_network(cidr_ip)
            result += [str(ip) for ip in network]
        return result

    if 'Database' in config:
        db_directory = config['Database'].get('db_directory', db_directory)
        db_file = config['Database'].get('db_file', db_file)
    if 'Global' in config:
        minutes_to_keep = config['Global'].getint('minutes_to_keep', minutes_to_keep)
        local_ips = config['Global'].get('local_ips', local_ips)
    local_ip_list = local_ips_to_ip_list(local_ips)

    pattern = (r'(\b\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b).*'
               r'cyrus/imap.*login:.*'
               r'\[(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)\].*'
               r'User logged in')

    db_path = os.path.join(db_directory, db_file)
    # Check if the directory exists, and if not, create it
    if not os.path.exists(db_directory):
        os.makedirs(db_directory, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                      (time TEXT, ip TEXT PRIMARY KEY)''')
    conn.commit()

    logfile = '/var/log/messages'
    with io.open(logfile, 'r', buffering=1) as file:
        # Jump to the end of the file
        file.seek(0, io.SEEK_END)

        # Read the last 5000 lines
        lines = deque(maxlen=5000)
        while len(lines) < 5000:
            line = file.readline()
            if not line:
                break
            lines.append(line)

        # Now, continuously monitor the file for new lines
        while True:
            line = file.readline()
            if not line:  # No new line yet, let's wait a bit
                time.sleep(0.1)
                continue
            else:
                lines.append(line)

            # Process the lines
            for line in lines:
                match = re.search(pattern, line)
                if match:

                    log_time_str, ip_address = match.groups()
                    if ip_address not in local_ip_list:
                        log_time_str += " " + str(datetime.now().year)
                        log_time_dt = datetime.strptime(log_time_str, "%b %d %H:%M:%S %Y")
                        log_time = log_time_dt.strftime("%Y-%m-%d %H:%M:%S")

                        time_threshold = datetime.now() - timedelta(minutes=minutes_to_keep)
                        cursor.execute("DELETE FROM logs WHERE time < ?",
                                       (time_threshold.strftime("%Y-%m-%d %H:%M:%S"),))
                        conn.commit()

                        cursor.execute("REPLACE INTO logs (time, ip) VALUES (?, ?)", (log_time, ip_address))
                        conn.commit()

            lines.clear()


if __name__ == '__main__':
    read_args()
    if args.daemon:
        myname = os.path.basename(sys.argv[0])
        pidfile = '/run/%s.pid' % myname  # any name
        daemon = Daemonize(app=myname, pid=pidfile, action=main)
        daemon.start()
    else:
        main()
