# NetworkMonitor
Monitor Network Services and Status, Send Alerts, and Log Data to a DB. Neat and Easy.
Comes in two parts:

-   A monitor
-   A report generator (should be scheduled using cron or a similar service).

## Setup
Configure a PostgreSQL Server with remote DB access (if you just want to use localhost, then skip this). 

Setup each application via command line (look at email and db arg groups).

For ease of use (on a secure network), you should use the root postgreSQL account (postgres).

Also don't forget to configure e-mail for the report generator.

## Usage
For help just run with -h

## Licence
See Licence file

## Dependency's

-   Python 2.7
-   Keyring (https://bitbucket.org/kang/python-keyring-lib) (included)
-   pg8000 (http://pybrary.net/pg8000/) (included)
-   SimpleMonitor (http://jamesoff.net/site/code/simplemonitor)