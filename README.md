# f2b-auto-ignorelist
Prevent Fail2Ban from blocking users who changed their password a limited time ago

I started this project because I was in the situation that again and again I had to manually add entries to ignoreip.
This happened because users who changed their password were blocked by e-mail clients which tried to login again and again with the old password.
And this happened because these users were not fast enough to update their passwords on all devices.

At the moment the project mainly consists of two scripts: 
One is a daemon which watches the log file in /var/log/messages and checks valid logins during the last minutes. The time range has to be given as a parameter.

The other one is the script which has to be defined in "ignorecommand" in the fail2ban configuration file jail.local.


