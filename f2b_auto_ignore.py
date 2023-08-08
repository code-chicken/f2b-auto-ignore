#!/usr/bin/python
from daemonize import Daemonize
import re
import subprocess
import sqlite3
import os, sys
from datetime import datetime, timedelta

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <minutes>")
        sys.exit(1)

    minutes_to_keep = int(sys.argv[1])

    pattern = (r'(\b\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\b).*'
               r'cyrus/imap.*login:.*'
               r'\[(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)\].*'
               r'User logged in')

    conn = sqlite3.connect('/var/lib/f2b_auto_ignore/login_success.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS logs
                      (time TEXT, ip TEXT PRIMARY KEY)''')
    conn.commit()

    with subprocess.Popen(['tail', '-F', '/var/log/messages'], stdout=subprocess.PIPE, universal_newlines=True) as process:
        for line in iter(process.stdout.readline, ""):
            match = re.search(pattern, line)
            if match:
                log_time_str, ip_address = match.groups()
                log_time_str += " " + str(datetime.now().year)
                log_time_dt = datetime.strptime(log_time_str, "%b %d %H:%M:%S %Y")
                log_time = log_time_dt.strftime("%Y-%m-%d %H:%M:%S")

                time_threshold = datetime.now() - timedelta(minutes=minutes_to_keep)
                cursor.execute("DELETE FROM logs WHERE time < ?", (time_threshold.strftime("%Y-%m-%d %H:%M:%S"),))
                conn.commit()

                cursor.execute("REPLACE INTO logs (time, ip) VALUES (?, ?)", (log_time, ip_address))
                conn.commit()

# The pid file ensures that only one instance of the daemon runs
#pid = "/tmp/log_watcher.pid"
#daemon = Daemonize(app="log_watcher", pid=pid, action=main)
#daemon.start()

if __name__ == '__main__':
        myname=os.path.basename(sys.argv[0])
        pidfile='/tmp/%s' % myname       # any name
        daemon = Daemonize(app=myname,pid=pidfile, action=main)
        daemon.start()

