import os
import sys
import blob

def extract_date_from_filename(filename):
    # Find the position of the second period and the next space after it
    second_period_pos = filename.find('.', filename.find('.') + 1)
    next_space_pos = filename.find(' ', second_period_pos)

    if second_period_pos != -1 and next_space_pos != -1:
        date_part = filename[second_period_pos + 1:next_space_pos]
        return date_part
    else:
        return None

def process_directory(directory):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if not filename.endswith('.py'):
                if not filename.endswith('.pyo'):
                    print filename
                    date_part = extract_date_from_filename(filename)
                    unserialized_blob = blob.load_from_file(filename)

                    blob_data = blob.dump_to_dict(unserialized_blob)

                    output_file = filename + ".py"
                    with open(output_file, "w") as f:
                        f.write('blob = ' + blob_data)
                        
                    # if date_part:
                    #    print("Date part of the file name in '{}': {}".format(filename, date_part))
                    #else:
                    #    print("Date part not found in the file name of '{}'.".format(filename))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py directory")
        sys.exit(1)

    directory = sys.argv[1]

    if not os.path.isdir(directory):
        print("Error: The given path is not a directory.")
        sys.exit(1)

    process_directory(directory)
