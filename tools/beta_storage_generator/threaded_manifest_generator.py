# Code by Cystface-man / Shefben
# With Help From YMGVE
# And Testing By Pmein1
# Created: 10/24/2023
# Modified: 10/27/2023
# version: Beta 2 (threaded)

import os
import struct
import zlib
import pickle
import re
import glob

from multiprocessing import Pool


def expand_wildcards_in_minfootprint():
    filename='minfootprint.txt'
    non_wildcard_lines = []
    wildcard_lines = []
    
    # Read and categorize lines as wildcard or non-wildcard
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if '*' in line:
                wildcard_lines.append(line)
            else:
                non_wildcard_lines.append(line)

    # Expand wildcard lines
    expanded_lines = []
    for line in wildcard_lines:
        path_pattern = os.path.join(directory_path, line)  # Assuming directory_path is defined globally or passed as a parameter
        expanded_lines.extend(glob.glob(path_pattern, recursive=True))

    # Sort expanded lines
    expanded_lines.sort()

    # Merge non-wildcard and expanded lines, maintaining alphabetical order
    all_lines = non_wildcard_lines + expanded_lines

    # Write merged lines back to file
    with open('minfootprint_temp.txt', 'w') as file:
        for line in all_lines:
            file.write(line + '\n')


def load_special_flags(filename='special_file_flags.ini'):
    """
    Load special flags from the given file and return as a dictionary.
    """
    flags = {}
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split('=')
                if len(parts) == 2:
                    path, flag_value = parts
                    flag_value = int(flag_value, 16)  # convert hex string to int

                    # Check if path ends with an asterisk
                    if path.endswith("*"):
                        path = path[:-1]  # Remove the asterisk from path in memory
                        for root, dirs, files in os.walk(path):
                            for dir in dirs:
                                flags[os.path.join(root, dir)] = flag_value
                            for file in files:
                                flags[os.path.join(root, file)] = flag_value
                    else:
                        flags[path] = flag_value
    return flags

def parse_minfootprint_file(filename='minfootprint.txt'):
    """
    Parse the 'minfootprint.txt' file and return a list of relative file paths.
    """
    file_paths = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                file_path = line.strip()
                if file_path:
                    file_paths.append(file_path)
    return file_paths

def process_file_chunk(args):
    file_path, chunk_size = args
    compressed_chunks = []
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            # NOTE: UNCOMMENT TO ENABLE COMPRESSION/DECOMPRESSION
            compressed_chunk = chunk  # zlib.compress(chunk)
            compressed_chunks.append(compressed_chunk)
    return compressed_chunks

def generate_gcf(directory_path, app_id, app_version, fingerprint):
    special_flags = load_special_flags()
    manifest_data = bytearray()
    filename_string = ""  # Root directory always starts with '00'
    node_index = 0  # Initialize node index (0 is reserved for root)
    file_count = 0  # Initialize file count
    dat_file_data = []
    index_data = {}
    file_index = []
    gcfdircopytable = bytearray()
    hex_fingerprint = struct.pack('4s', fingerprint.encode('ascii'))

    # Load the list of file paths from "minfootprint.txt"
    # First check to see if there is an expanded wildcard temporary footprint file
    if os.path.isfile("minfootprint_temp.txt"):
        minfootprint_file_paths = parse_minfootprint_file("minfootprint_temp.txt")
    else:
        minfootprint_file_paths = parse_minfootprint_file()
    
    # Define a structure to hold directory and file data
    items = []

    for root, dirs, files in os.walk(directory_path):
        if root == directory_path:
            parent_index = 0xffffffff
        else:
            parent_index = 0 if os.path.dirname(root) == directory_path else [item['index'] for item in items if item['path'] == os.path.relpath(os.path.dirname(root), directory_path)][0]

        relative_root = os.path.relpath(root, directory_path)
        
        items.append({
            'type': 'dir',
            'path': relative_root,
            'parent': parent_index,
            'index': node_index,
        })
        node_index += 1
        
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), directory_path)
            items.append({
                'type': 'file',
                'path': relative_path,
                'parent': [item['index'] for item in items if item['path'] == os.path.relpath(root, directory_path)][0],
                'index': node_index,
            })
            node_index += 1

    # Process items and generate manifest
    for item in items:
        parent_index = item['parent']
        siblings = [i for i in items if i['parent'] == parent_index]
        current_index = item['index']

        next_index = 0
        for idx, sibling in enumerate(siblings):
            if sibling['index'] == current_index and idx < len(siblings) - 1:
                next_index = siblings[idx+1]['index']
                break

        if item['type'] == 'dir':
            current_dir_index = item['index']
            
            # Child count
            child_count = sum(1 for i in items if i['parent'] == current_dir_index)
            
            # Child index
            children = [i for i in items if i['parent'] == current_dir_index]
            child_index = children[0]['index'] if children else 0
            
            # Add directory to manifest
            manifest_data += struct.pack("<IIIIIII", len(filename_string), child_count, 0xffffffff, 0x00000000, parent_index, next_index, child_index)
            
            # Add directory to filename string
            if item['path'] != "." :
                directory_name = item['path'].split(os.sep)[-1]
                filename_string += directory_name + "\x00"
            else :
                filename_string = "\x00"

            print("Processed directory: {}, Index: {}, Parent Index: {}, Next Index: {}, Child Index: {}".format(item['path'], current_dir_index, parent_index, next_index, child_index))
            
        elif item['type'] == 'file':
            file_count += 1
            file_index.append(item['index'])
            flag = special_flags.get(item['path'], 0x0000400a)
            
            # Processing for gcfdircopytable
            if item['path'] in minfootprint_file_paths:
                print("file {} added to minfootprint table!".format(item['path']))
                gcfdircopytable += struct.pack("<I", item['index'])
            
            # Add file to manifest using the special flag
            manifest_data += struct.pack("<IIIIIII", len(filename_string), 0, file_count, flag, parent_index, next_index, 0)

            print("Processing file: {}, Index: {}, Parent Index: {}, File Count: {}, Next File Index: {}".format(item['path'], item['index'], parent_index, file_count, next_index))
            
            # Process the file in chunks and compress each chunk
            file_path = os.path.join(directory_path, item['path'])
            content_size = os.path.getsize(file_path)
            chunk_size = 0x10000
            pool = Pool()
            compressed_chunks = pool.map(process_file_chunk, [(file_path, chunk_size)])
            pool.close()
            pool.join()
            
            # Flatten the list of compressed chunks
            compressed_data = ''.join(compressed_chunks[0])
            
            # Update index data
            index_data[file_count] = {
                'total_chunks': len(compressed_chunks[0]),
                'chunks_info': [{
                    'chunkID': i,
                    'offset': i * chunk_size,
                    'length': len(chunk)
                } for i, chunk in enumerate(compressed_chunks[0])]
            }
            
            dat_file_data.append(compressed_data)
            
            print("Processed {} chunks for file: {}".format(len(compressed_chunks[0]), item['path']))  # Print number of chunks processed for the current file

            # Add file to filename string
            filename_string += item['path'].split(os.sep)[-1] + "\x00"
    
    # After processing all the chunks, concatenate them into a single string
    dat_file_data = ''.join(dat_file_data)
    
    if not gcfdircopytable:
        for i in range(file_count):        
            gcfdircopytable += struct.pack("<I", file_index[i])
        
    filename_string = filename_string.encode("utf-8")
    
    while len(filename_string) % 4 != 0:
        filename_string += b"\x00"            
    # generate header of manifest file
    manif_version = 3 # Manifest Version
    manif_appid = app_id # application id
    manif_appversion = int(app_version) # application version
    manif_num_nodes = item['index']+1 # total node count
    manif_file_count = len(file_index) # total file count
    manif_dirnamesize = len(filename_string) # total size of the filename string with the null bytes
    manif_info1count = 1 # ymgve: 1, just 1
    manif_copycount = len(file_index) # Files that should be copied from the cache to the local drive
    manif_localcount = 0 # also known as user config files / files that should not be written over using cache files
    manif_compressedblocksize = 0x8000 # 8 byte compressed blocks
    manif_totalsize = 0x38 + manif_num_nodes * 0x1c + manif_dirnamesize + (manif_info1count + manif_num_nodes) * 4 + manif_copycount * 4 + manif_localcount * 4

        
    manif = struct.pack("<IIIIIIIIIIIIII", manif_version, manif_appid, manif_appversion, manif_num_nodes, manif_file_count, manif_compressedblocksize, 
                        manif_totalsize, manif_dirnamesize, manif_info1count, manif_copycount, manif_localcount, 2, 0, 0)
        
    manif = manif[:0x1c] + struct.pack("<I", len(filename_string)) + manif[0x20:]
        
    hashtable = struct.pack("<I", 1)
    for idx in range(manif_num_nodes-1):
        hashtable += struct.pack("<I", idx)
    hashtable += struct.pack("<I", (manif_num_nodes - 1) | 0x80000000)
    
    final_manifest = manif + manifest_data + filename_string + hashtable + gcfdircopytable
    
    # Checksums for manifest itself (no file checksums):
    final_manifest = final_manifest[:0x30] + '\x00' * 8 + final_manifest[0x38:]
    checksum_value = hex_fingerprint + struct.pack("<I", zlib.adler32(str(final_manifest), 0) & 0xFFFFFFFF)
    final_manifest = final_manifest[:0x30] + checksum_value + final_manifest[0x38:]

    
    with open("{}_{}.manifest".format(app_id, app_version), "wb") as f:
        f.write(final_manifest)
        
    # Saving the .dat file and .index file
    with open("{}_{}.dat".format(app_id, app_version), "wb") as f:
        f.write(dat_file_data)

    with open("{}_{}.index".format(app_id, app_version), "wb") as f:
        pickle.dump(index_data, f)

if __name__ == "__main__":
    import sys
        
    if (len(sys.argv) < 2 or (len(sys.argv) < 5 and sys.argv[1].lower() != "help")) :
        print("Usage: python manifest_generator.py <directory_path> <app_id> <app version> <unique 4 character fingerprint>")
        print("Or for general usage and help use: python manifest_generator.py help")
        print("For help using special_file_flags.ini use: python manifest_generator.py help flags")
        print("For help using minfootprint.txt use: python manifest_generator.py help footprint")
        sys.exit(1)
        
    if (sys.argv[1].lower() == "help" and sys.argv[2].lower() == "flags"):
        print("special_file_flags.ini Information:")
        print("NOTE: All Directories already automatically are flagged as such (0x0) and should not be included in the hex additiion")
        print("Files are automatically are flagged with 0x4000a as well, do not include these in your flag calcuation!")
        print("")
        print("Available Flags (hex):")
        print(" Executable_File = 0x800")
        print(" Hidden_File = 0x400")
        print(" ReadOnly_File = 0x200")
        print(" Encrypted_File = 0x100")
        print(" Purge_File = 0x80")
        print(" Backup_Before_Overwriting = 0x40")
        print(" NoCache_File = 0x20")
        print(" Locked_File = 0x8")
        print(" Launch_File = 0x2")
        print(" Configuration_File = 0x1")
        print("")
        print("How to add multiple Flags:")
        print("Example:  We want a file to be backed up and readonly.")
        print("the calculation is: 0x40 + 0x200 = 0x640")
        print("")
        print("The format of the special_file_flags.ini file should be in the format of 1 file and flag per line.")
        print("")
        print("<file path without root directory>=0x<flag hex>")
        print("")
        print("Example ini:")
        print("")
        print("# Apply a flag to a specific file (configuration file)")
        print("valve/sprites/shellchrome.spr=0x1")
        print(""
        print("# Apply a flag to a specific directory (non-recursively)")
        print("valve/maps=0x0F1C")
        print("")
        print("# Apply a flag recursively to all files and directories under a certain path")
        print("valve/textures/*=0x40")
        print("")        
        print("# Another file with a different flag (executable and readonly)")
        print("hl.exe=0xa00")
        print("")
        sys.exit(1)
    elif (sys.argv[1].lower() == "help" and sys.argv[2].lower() == "footprint"):
        print("minfootprint.txt Information:")
        print("The format of the file minfootprint.txt should be like this example:")
        print("valve\sprites\shellchrome.spr")
        print("valve\woncomm.lst")
        print("hw.dll")
        sys.exit(1)
    elif (sys.argv[1].lower() == "help") :
        print("This tool is used to take raw files and generate a manifest that can be sent to beta 1 and beta 2 steam clients.")
        print("It also takes each file, compresses it and adds it to a storage (.dat file) for later retrieval on the server when the client requests a certain file id")
        print("and generates a \'.index\' file which holds where in the \'.dat\' file a specific fileid is and how big that file is in there.")
        print("App_id Must be a number with NO letters or special characters.")
        print("App version must also be a number, do not use letters, periods or special characters.")
        print("The unique 4 character finger print is used for identification by steam to determine which cache it is looking for.")
        print("The 4 characters can be anything (letters, numbers, special characters) but must be exactly 4 characters.")
        print("")
        print("------------------------------------------------------------------------------------------------------------")
        print("Usage: python manifest_generator.py <directory_path> <app_id> <app version> <unique 4 character fingerprint>")
        print("Or for help use: python manifest_generator.py help")
        sys.exit(1)

    # This function will expand ALL wildcard dir files into a temporary miinfootprint file.
    print("...Expanding Wildcard (*) entries (if any) in minfootprint.txt...")
    expand_wildcards_in_minfootprint()

    directory_path = sys.argv[1]
    app_id = int(sys.argv[2], 16)  # Taking app_id in hex format from command line argument
    app_version = "".join(re.findall(r'\d', sys.argv[3]))  # Extracting only numbers from app_version
    fingerprint = sys.argv[4]
    generate_gcf(directory_path, app_id, app_version, fingerprint)
