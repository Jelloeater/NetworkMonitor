# NetworkMonitor
Monitor Network Services and Status, Send Alerts, and Log Data to a DB. Neat and Easy.
Comes in three sections:

-   A monitor
-   A report generator (that can also be scheduled externally).
-   A database TUI front end (for configuring monitoring lists)

## Setup
-   Configure a PostgreSQL Server with remote DB access (if you just want to use localhost, then skip this). 
-   Setup each application via command line (look at email and db arg groups).
-   For ease of use (on a secure network), you should use the root postgreSQL account (postgres).
-   Also don't forget to configure e-mail for the report generator.
-   Add hosts to the monitoring list via the TUI.

## Usage
-   Setup first
-   Run with -m
-   Feel sad when services go down.
-   Feel happy when they go back up.
-   For help just run with -h

## Licence
See Licence file

## Dependency's
### Applications
-   Python 2.7
-   N-map (http://nmap.org)

### Libs
-   Keyring (https://bitbucket.org/kang/python-keyring-lib) (included)
-   pg8000 (http://pybrary.net/pg8000/) (included)
-   python-nmap (http://xael.org/norman/python/python-nmap/)
-   gmail (https://pypi.python.org/pypi/gmail/0.5)

# Credits
-   SimpleMonitor (http://jamesoff.net/site/code/simplemonitor) for framework and inspiration