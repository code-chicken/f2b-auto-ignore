# f2b-auto-ignore
Prevent Fail2Ban from blocking users who changed their password a limited time ago.

I started this project because I was in the situation that again and again I had to manually add entries to ignoreip in the fail2ban configuration file jail.local.
This happened because users who changed their password were blocked by e-mail clients trying to login multiple times in a short time with the old password.
This happened because these users were not fast enough to update their password on all devices.

At the moment the project mainly consists of two scripts:
One is a daemon which watches the log file in /var/log/messages and searches for valid logins during the past minutes. The amount of minutes has to be supplied as a numeric parameter. At the moment this script only looks for successful cyrus-imap logins, which should not be a problem to be changed.

The other one is a script which has to be defined in "ignorecommand" in the fail2ban configuration file jail.local. This script will look for an IP which has been found by the daemon mentioned before.

The result is, within a limited time, a user who has successfully logged in some time before will not be blocked by the firewall when  - for example - some email apps still try to login with the old credentials.

## Requirements
* Python Daemonize library


