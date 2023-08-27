import os
import re

from globalvars import config

# Get the absolute path of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the new path for DocumentRoot and <Directory>
new_path = os.path.join(script_dir, 'files', 'webroot')

# Define the path to the Apache configuration file
apache_conf_path = os.path.join(script_dir, 'files', 'apache24', 'conf', 'httpd.conf')

# Regular expression patterns for matching relevant lines
docroot_pattern = r'^\s*DocumentRoot\s+"[^"]*"'
dir_pattern = r'^\s*<Directory\s+"[^"]*">'

# Function to check if a line contains the path
def contains_path(line, path):
    return path in line

# Function to modify paths and save the changes
def modify_apache_config(file_path):
    new_lines = []
    config_modified = False
    updated_signature = '{}'.format(config['http_signature'])

    with open(file_path, 'r') as f:
        for line in f:
            docroot_match = re.match(docroot_pattern, line)
            dir_match = re.match(dir_pattern, line)

            if docroot_match:
                new_line = 'DocumentRoot "{}"'.format(new_path)
                new_lines.append(new_line)
                config_modified = True
            elif dir_match:
                new_line = '<Directory "{}">'.format(new_path)
                new_lines.append(new_line)
                config_modified = True
            elif line.strip().startswith('Listen '):
                new_line = 'Listen {}:{}'.format(config['http_ip'], config['http_port'])
                new_lines.append(new_line)
                config_modified = True
            elif line.strip().startswith('SecServerSignature'):
                # Replace the existing line with the updated value
                new_line = 'SecServerSignature {}'.format(updated_signature)
                new_lines.append(new_line)
                config_modified = True
            elif re.match(r'^\s*QS_SrvMaxConn\s+', line):
                # Replace QS_SrvMaxConn line
                new_line = 'QS_SrvMaxConn {}'.format(config['http_maxconnections'])
                new_lines.append(new_line)
                config_modified = True
            elif line.strip().startswith('ServerAdmin'):
                new_line = 'ServerAdmin {}'.format(config['admin_email'])
                new_lines.append(new_line)
                config_modified = True
            else:
                new_lines.append(line.rstrip())  # Remove extra newline

    if config_modified:
        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))
        print("Apache configuration file modified successfully.")
    else:
        print("No relevant configuration found.")


def check_config():
    # Modify the Apache configuration file
    modify_apache_config(apache_conf_path)
