import BaseHTTPServer
import SimpleHTTPServer
import SocketServer
import subprocess
import os
import msvcrt
import threading
import mimetypes
import urlparse
import urllib
import ssl
import zlib
import time
from steamemu.config import save_config_value
from steamemu.config import read_config

config = read_config()

if config['http_disable'] is 'False' :
    os._exit(0)

# Define if SSL should be enabled
ENABLE_SSL = 1 if config['ssl_enable'] is 'True' else 0
SSL_CERTIFICATE = config['ssl_certificatepem']
SSL_KEY = config['ssl_privatekeypem']

# Set the PHP executable path. Adjust this path according to your system.
PHP_EXECUTABLE = config['http_php_path'] + 'php-cgi.exe'
#PHP_EXECUTABLE = r'./files//php//php-cgi.exe'
# Set the ip and port number for your server.
IP = config['http_ip']
PORT = int(config['http_port'])

# Define the web root directory.
WEB_ROOT = r'webroot' #config['http_webroot']

ERROR_PAGES = {
    404: '404.html',
    500: '500.html'
}

# Define the rate limit parameters (requests per minute)
RATE_LIMIT = int(config['http_ratelimit_connection_limit'])
RATE_LIMIT_PERIOD = int(config['http_ratelimit_period'])  # seconds

# Dictionary to track request counts per IP
request_counts = {}
request_times = {}

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def send_auto_index(self, dirpath):
        # Generate a basic HTML auto-index page
         #os.listdir(os.path.abspath(os.path.join(WEB_ROOT, "." + self.path +dirpath)))
        files = os.listdir(os.path.join(WEB_ROOT, "." + self.path))
        files_html = ''.join(['<li><a href="{0}">{0}</a></li>'.format(f) for f in files])
        auto_index_html = '<html><body><ul>{}</ul></body></html>'.format(files_html)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(auto_index_html)))
        self.end_headers()
        self.wfile.write(auto_index_html)
        
    def handle_htaccess(self, path):
        # Check if .htaccess exists in the directory
        htaccess_path = os.path.join(WEB_ROOT, path, '.htaccess')
        if os.path.exists(htaccess_path):
            with open(htaccess_path, 'r') as htaccess_file:
                directives = htaccess_file.readlines()

            for directive in directives:
                # Handle .htaccess directives here
                pass
            
    def redirect_to_https(http_handler):
        if ENABLE_SSL and http_handler.headers.get('X-Forwarded-Proto', 'http') == 'http':
            new_location = 'https://' + http_handler.headers['Host'] + http_handler.path
            http_handler.send_response(301)
            http_handler.send_header('Location', new_location)
            http_handler.end_headers()
        else:
            http_handler.send_error(403, "Forbidden")
            
    def rate_limit_exceeded(self, ip):
        # Check if the rate limit for the IP has been exceeded
        current_time = int(time.time())
        if ip in request_times and current_time - request_times[ip] < RATE_LIMIT_PERIOD:
            request_counts[ip] += 1
            return request_counts[ip] > RATE_LIMIT
        else:
            request_times[ip] = current_time
            request_counts[ip] = 1
            return False
        
    def send_error_response(self, code, message=None):
        error_page = ERROR_PAGES.get(code)
        if error_page:
            self.send_custom_error_page(code, error_page)
        else:
            self.send_default_error_response(code, message)


    def send_custom_error_page(self, code, error_page):
        error_path =os.path.join(WEB_ROOT+"\\error_pages\\", error_page)
      
        if os.path.exists(error_path):
            
            with open(error_path, 'rb') as f:
                content = f.read()

            self.send_response(code)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(code)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write("Error {} - {}".format(code, self.responses[code][0]))


    def send_compressed_response(self, content, content_type):
        compressed_content = zlib.compress(content, 9)

        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(compressed_content)))
        self.end_headers()

        self.wfile.write(compressed_content)

    def send_gzip_file(self, filepath):
        if os.path.exists(filepath):
            
            with open(filepath, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', self.guess_type(filepath))
            self.send_compressed_response(content)
            
        else:
            
            self.send_error_response(404, "File Not Found")

    def do_GET(self):
        if '?' in self.path:
            
            # If the URL contains query parameters, extract them
            path, query_string = self.path.split('?', 1)
            self.path = path
            self.query_string = query_string
        else:
            self.query_string = ''

        ip = self.client_address[0]
        if self.rate_limit_exceeded(ip):
            self.send_error_response(429, "Rate Limit Exceeded")
            return
        
        if ENABLE_SSL and self.headers.get('X-Forwarded-Proto', 'http') == 'http':
            redirect_to_https(self)
            return
        
        print("Received GET request:")
        print("Path:", self.path)
        print("Query String:", self.query_string)

        if self.path.endswith('.php'):
            self.handle_php_cgi(method='GET', accept_encoding=self.headers.get('Accept-Encoding'))
        elif self.path.endswith('/'):
            dir_path = os.path.abspath(os.path.join(WEB_ROOT, "." + self.path )) 
            index_php_path = os.path.join(dir_path, "index.php") #os.path.abspath(os.path.join(dir_path, ''))
            
            index_html_path = os.path.join(dir_path, 'index.html')
            #print index_php_path
            if os.path.exists(index_php_path):
                #self.handle_php_cgi(method='GET', accept_encoding=self.headers.get('Accept-Encoding'))
                new_location = self.path + 'index.php'
                self.send_response(301)
                self.send_header('Location', new_location)
                self.end_headers()
                return
            elif os.path.exists(index_html_path):
                self.send_gzip_file(index_html_path)
                return

            self.send_auto_index(dir_path)
        else:
            self.send_gzip_file(os.path.join(WEB_ROOT, '.' + self.path))

    def do_HEAD(self):
        if '?' in self.path:
            # If the URL contains query parameters, extract them
            path, query_string = self.path.split('?', 1)
            self.path = path
            self.query_string = query_string
        else:
            self.query_string = ''

        ip = self.client_address[0]
        
        if self.rate_limit_exceeded(ip):
            self.send_error_response(429, "Rate Limit Exceeded")
            return

        if ENABLE_SSL and self.headers.get('X-Forwarded-Proto', 'http') == 'http':
            redirect_to_https(self)
            return

        print("Received HEAD request:")
        print("Path:", self.path)
        print("Query String:", self.query_string)

        if self.path.endswith('.php'):
            self.handle_php_cgi(method='HEAD', accept_encoding=self.headers.get('Accept-Encoding'))
        else:
            self.send_response(200)
            self.send_header('Content-type', self.guess_type(self.path))
            self.end_headers()

    def do_POST(self):
        if '?' in self.path:
            # If the URL contains query parameters, extract them
            path, query_string = self.path.split('?', 1)
            self.path = path
            self.query_string = query_string
        else:
            self.query_string = ''

        content_length = int(self.headers.getheader('content-length', 0))
        post_data = self.rfile.read(content_length)

        ip = self.client_address[0]
        if self.rate_limit_exceeded(ip):
            self.send_error_response(429, "Rate Limit Exceeded")
            return
        
        if ENABLE_SSL and self.headers.get('X-Forwarded-Proto', 'http') == 'http':
            redirect_to_https(self)
            return

        print("Received POST request:")
        print("Path:", self.path)
        print("Query String:", self.query_string)
        print("POST Data:", post_data)

        if self.path.endswith('/'):
            dir_path = os.path.join(WEB_ROOT, self.path)
            index_php_path = os.path.join(dir_path, 'index.php')
            index_html_path = os.path.join(dir_path, 'index.html')

            if os.path.exists(index_php_path):
                self.handle_php_cgi(method='GET', accept_encoding=self.headers.get('Accept-Encoding'))
                return
            elif os.path.exists(index_html_path):
                self.send_gzip_file(index_html_path)
                return

            self.send_auto_index(dir_path)
        elif self.path.endswith('.php'):
            self.handle_php_cgi(method='POST', accept_encoding=self.headers.get('Accept-Encoding'))
        else:
            self.send_gzip_file(os.path.join(WEB_ROOT, '.' + self.path))


    def handle_php_cgi(self, method=None, post_data=None, accept_encoding=None):

        if ENABLE_SSL and self.headers.get('X-Forwarded-Proto', 'http') == 'http':
            redirect_to_https(self)
            return
        script_filename = os.path.abspath(os.path.join(WEB_ROOT, '.' + self.path))
        relative_path = os.path.relpath(script_filename, WEB_ROOT)
        
        # Build the CGI environment variables
        env = {
            # Other environment variables...
            'REQUEST_METHOD': method,
            'SCRIPT_FILENAME': os.path.join(WEB_ROOT, '.' + self.path),
            'SCRIPT_NAME': self.path,
            'QUERY_STRING':  self.query_string,
            'REQUEST_URI': self.path + ('?' + self.query_string if self.query_string else ''),
            'DOCUMENT_ROOT': WEB_ROOT,
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': 'SimpleHTTP/0.6 Python/2.7',
            'REDIRECT_STATUS': '200',
            'SERVER_NAME': self.server.server_address[0],
            'SERVER_PORT': str(self.server.server_address[1]),
            'SERVER_PROTOCOL': self.request_version,
        }
        env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        
        if accept_encoding:
            env['HTTP_ACCEPT_ENCODING'] = accept_encoding
            
        if post_data :
            env['CONTENT_LENGTH'] = str(len(post_data))
            
        # Add the PHP superglobals ($_SERVER, $_GET, $_POST, etc.) to the environment
        for key, value in self.headers.items():
            if key.startswith('HTTP_'):
                env_key = key.replace('HTTP_', '').replace('_', '-').upper()
                env['HTTP_' + env_key] = value
                env['_' + env_key] = value

        # Set the REQUEST_METHOD in the environment
        if method:
            env['REQUEST_METHOD'] = method

        # Set the QUERY_STRING in the environment and parse it to get the GET variables
        if '?' in self.path:
            path, query_string = self.path.split('?', 1)
            env['QUERY_STRING'] = query_string

            # Parse the query string to get the GET variables and add them to the environment
            get_params = urllib.parse.parse_qs(query_string)
            
            for key, value in get_params.items():
                env['GET_' + key.upper()] = value[0]
        else:
            path = self.path

        # Set the SCRIPT_FILENAME and SCRIPT_NAME in the environment
        env['SCRIPT_FILENAME'] = script_filename
        env['SCRIPT_NAME'] = '/' + relative_path
        
        content_type = mimetypes.guess_type(self.path)[0] or 'application/octet-stream'

        # Set the CONTENT_TYPE based on the determined content type
        if method == 'POST':
            env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
        else:
            env['CONTENT_TYPE'] = content_type
        print "abspath: "+ os.path.abspath(os.path.join(WEB_ROOT, self.path))
        for header_name, header_value in self.headers.items():
            env['HTTP_' + header_name.replace('-', '_').upper()] = header_value
            
        php_cmd = [
            PHP_EXECUTABLE, '-q', os.path.join(WEB_ROOT, "." + self.path)
        ]
        
        process = subprocess.Popen(php_cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        if post_data:
            process.stdin.write(post_data.encode('utf-8'))
        process.stdin.close()

        stdout, stderr = process.communicate()

        # Send the PHP script's output as the response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(stdout)))
        self.end_headers()
        self.wfile.write(stdout)
                
class ThreadedHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


def run_server():
    server_address = (IP, PORT)
    httpd = ThreadedHTTPServer(server_address, MyHandler)

    if ENABLE_SSL:
        httpd.socket = ssl.wrap_socket(httpd.socket, certfile=SSL_CERTIFICATE, keyfile=SSL_KEY, server_side=True)

    print("Stmserver HTTP Server Is Running On Port {}...".format(PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server is shutting down...")
        httpd.shutdown()


def watchescape_thread():
    while True:
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # 27 is the ASCII code for Escape
            os._exit(0)


if __name__ == "__main__":
    thread2 = threading.Thread(target=watchescape_thread)
    thread2.daemon = True
    thread2.start()

    run_server()
