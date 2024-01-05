import logging

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

log = logging.getLogger('pyftpdlib')


def create_ftp_server(directory, address = "0.0.0.0", port = 21):
    # logging.getLogger('pyftpdlib').disabled = True #.removeHandler(sys.stdout) # .setLevel(logging.CRITICAL)  # or ERROR, CRITICAL
    logger = logging.getLogger('pyftpdlib')
    # logger.setLevel(logging.INFO)  # Set the desired logging level
    file_handler = logging.FileHandler('logs/pyftpdlib.log')
    logger.addHandler(file_handler)
    logger.propagate = False
    # Instantiate a dummy authorizer for managing 'virtual' users
    authorizer = DummyAuthorizer()

    # Enable anonymous access with specific permissions
    authorizer.add_anonymous(directory, perm = "elr")

    # Instantiate FTP handler class
    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a function to prevent access to subdirectories
    def is_subdirectory(path):
        # Split the path to check for subdirectories
        return len(path.split('/')) > 2

    # Override the FTPHandler function to limit to the given directory
    original_ftphandler = handler.ftp_LIST

    def new_ftp_LIST(self, path):
        if not path or path == '/' or not is_subdirectory(path):
            original_ftphandler(self, path)
        else:
            self.respond("550 Permission denied.")

    handler.ftp_LIST = new_ftp_LIST

    # Create FTP server and start serving
    server = FTPServer((address, port), handler)
    server.serve_forever()


# Usage example - Replace 'path/to/your/folder' with the path to the folder you want to serve
if __name__ == "__main__":
    create_ftp_server("files/beta1_ftp")