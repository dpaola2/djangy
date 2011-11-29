import socket

def fetch_url(host, url):
    """Fetch the headers and body of a URL from a given host.  Useful when a
    host recognizes virtual hosts that don't actually point to it in DNS."""

    s = socket.create_connection((host, 80)).makefile()
    s.write('GET %s HTTP/1.0\n\n' % url)
    s.flush()
    response = s.read()
    s.close()
    return response

def fetch_url_body(host, url):
    """Return just the body from fetch_url(host, url)"""

    response = fetch_url(host, url)
    n = response.index('\r\n\r\n') + 4
    return response[n:]

def fetch_url_headers(host, url):
    """Return just the headers from fetch_url(host, url), as a dictionary."""

    response = fetch_url(host, url)
    n = response.index('\r\n\r\n')
    headers_list = response[:n].split('\r\n')
    headers_dict = {'STATUS': headers_list[0].split(' ', 2)[1]}
    for header in headers_list:
        try:
            (k, v) = header.split(':', 1)
            headers_dict[k.strip()] = v.strip()
        except:
            pass

    return headers_dict
