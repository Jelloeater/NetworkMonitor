"""Network-related monitors for SimpleMonitor."""
import logging
import urllib2
from nmap import PortScanner


class MonitorHTTP():
    """Check an HTTP server is working right. """

    def __init__(self, url):
        self.url = url

    def run_test(self):
        # store the current default timeout (since it's global)
        http_response_code = 404
        try:
            http_response_code = urllib2.urlopen(self.url, timeout=1).code
        except ValueError:
            logging.warning('Invalid URL')
        except urllib2.URLError:
            logging.info(self.url + ' is down')
            return False

        if http_response_code == 200:
            return True
        else:
            return False

    def describe(self):
        """Explains what we do."""
        return "Checking that accessing %s returns HTTP/200 OK" % self.url


class MonitorTCP():
    """TCP port monitor"""

    def __init__(self, host, port):

        if host == "":
            raise RuntimeError("missing hostname")
        if port == "" or port <= 0:
            raise RuntimeError("missing or invalid port number")
        self.host = host
        self.port = port

    def run_test(self):
        """Check the port is open on the remote host"""
        ps = PortScanner()
        scan = ps.scan(hosts=self.host, ports=self.port)
        try:
            if scan['scan'][str(self.host)]['status']['state'] == 'up':
                return True
        except KeyError:  # If we cannot find the info in the key for the status, this means the host is down
            return False

    def describe(self):
        """Explains what this instance is checking"""
        return "checking for open tcp socket on %s:%d" % (self.host, self.port)

    def get_params(self):
        return self.host, self.port


class MonitorHost():
    """Ping a host to make sure it's up"""
    def __init__(self, host):
        self.host = host
        if host == "":
            raise RuntimeError("missing hostname")

    def run_test(self):
        scan = PortScanner().scan(self.host, arguments='-sn')
        try:
            if scan['scan'][str(self.host)]['status']['state'] == 'up':
                return True
        except KeyError:  # If we cannot find the info in the key for the status, this means the host is down
            return False

    def describe(self):
        """Explains what this instance is checking"""
        return "checking host %s is pingable" % self.host

