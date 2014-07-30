
"""Network-related monitors for SimpleMonitor."""

import urllib
import urllib2
import re
import os
import socket
import datetime



class MonitorHTTP():
    """Check an HTTP server is working right.
    
    We can either check that we get a 200 OK back, or we can check for a regexp match in the page.
    """

    url = ""
    regexp = None
    regexp_text = ""
    allowed_codes = []

    type = "http"

    def __init__(self, name, config_options):
        try:
            url = config_options["url"]
        except:
            raise RuntimeError("Required configuration fields missing")
        
        if config_options.has_key("regexp"):
            regexp = config_options["regexp"]
        else:
            regexp = ""
        if config_options.has_key("allowed_codes"):
            allowed_codes = [int(x.strip()) for x in config_options["allowed_codes"].split(",")]
        else:
            allowed_codes = []

        self.url = url
        if regexp != "":
            self.regexp = re.compile(regexp)
            self.regexp_text = regexp
        self.allowed_codes = allowed_codes

    def run_test(self):
        # store the current default timeout (since it's global)
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(5)
        start_time = datetime.datetime.now()
        end_time = None
        try:
            url_handle = urllib2.urlopen(self.url)
            end_time = datetime.datetime.now()
            load_time = end_time - start_time
            status = "200 OK"
            if hasattr(url_handle, "status"):
                if url_handle.status != "":
                    status = url_handle.status
            if status != "200 OK":
                self.record_fail("Got status '%s' instead of 200 OK" % status)
                socket.setdefaulttimeout(original_timeout)
                return False
            if self.regexp == None:
                self.record_success("%s in %0.2fs" % (status, (load_time.seconds + (load_time.microseconds / 1000000.2))))
                socket.setdefaulttimeout(original_timeout)
                return True
            else:
                for line in url_handle:
                    matches = self.regexp.search(line)
                    if matches:
                        self.record_success("%s in %0.2fs" % (status, (load_time.seconds + (load_time.microseconds / 1000000.2))))
                        socket.setdefaulttimeout(original_timeout)
                        return True
                self.record_fail("Got 200 OK but couldn't match /%s/ in page." % self.regexp_text)
                socket.setdefaulttimeout(original_timeout)
                return False
        except urllib2.HTTPError, e:
            if e.code in self.allowed_codes:
                if end_time != None:
                    load_time = end_time - start_time
                    self.record_success("%s in %0.2fs" % (status, (load_time.seconds + (load_time.microseconds / 1000000.2))))
                else:
                    self.record_success("%s" % status)
                socket.setdefaulttimeout(original_timeout)
                return True
            self.record_fail("HTTP error while opening URL: %s" % e)
            socket.setdefaulttimeout(original_timeout)
            return False
        except Exception, e:
            self.record_fail("Exception while trying to open url: %s" % e)
            socket.setdefaulttimeout(original_timeout)
            return False

    def describe(self):
        """Explains what we do."""
        if self.regexp == None:
            message = "Checking that accessing %s returns HTTP/200 OK" % self.url
        else:
            message = "Checking that accessing %s returns HTTP/200 OK and that /%s/ matches the page" % (self.url, self.regexp_text)
        return message

    def get_params(self):
        return (self.url, self.regexp_text, self.allowed_codes)


class MonitorTCP():
    """TCP port monitor"""

    host = ""
    port = ""
    type = "tcp"

    def __init__(self, host, port):
        """Constructor"""
        try:
            host = host
            port = int(port)
        except:
            raise RuntimeError("Required configuration fields missing")

        if host == "":
            raise RuntimeError("missing hostname")
        if port == "" or port <= 0:
            raise RuntimeError("missing or invalid port number")
        self.host = host
        self.port = port

    def run_test(self):
        """Check the port is open on the remote host"""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(5.0)
            s.connect((self.host, self.port))
        except:
            self.record_fail()
            return False
        s.close()
        self.record_success()
        return True

    def describe(self):
        """Explains what this instance is checking"""
        return "checking for open tcp socket on %s:%d" % (self.host, self.port)

    def get_params(self):
        return (self.host, self.port)


class MonitorHost():
    """Ping a host to make sure it's up"""

    host = ""
    ping_command = ""
    ping_regexp = ""
    type = "host"
    time_regexp = ""

    def __init__(self, host):
        """
        Note: We use -w/-t on Windows/POSIX to limit the amount of time we wait to 5 seconds.
        This is to stop ping holding things up too much. A machine that can't ping back in <5s is
        a machine in trouble anyway, so should probably count as a failure.
        """

        self.ping_command = "ping -c1 -t5 %s 2> /dev/null"
        self.ping_regexp = "bytes from"
        #XXX this regexp is only for freebsd at the moment; not sure about other platforms
        #XXX looks like Linux uses this format too
        self.time_regexp = "min/avg/max/stddev = [\d.]+/(?P<ms>[\d.]+)/"

        try:
            host = host
        except:
            raise RuntimeError("Required configuration fields missing")
        if host == "":
            raise RuntimeError("missing hostname")
        self.host = host

    def run_test(self):
        r = re.compile(self.ping_regexp)
        r2 = re.compile(self.time_regexp)
        success = False
        pingtime = 0.0
        try:
            process_handle = os.popen(self.ping_command % self.host)
            for line in process_handle:
                matches = r.search(line)
                if matches:
                    success = True
                else:
                    matches = r2.search(line)
                    if matches:
                        pingtime = matches.group("ms")
        except Exception, e:
            return False
        if success:
            if pingtime > 0:
                return "%sms" % pingtime
        else:
            return False

    def describe(self):
        """Explains what this instance is checking"""
        return "checking host %s is pingable" % self.host

    def get_params(self):
        return (self.host, )

