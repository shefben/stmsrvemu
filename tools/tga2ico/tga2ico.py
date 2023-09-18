import os
from PIL import Image

def convert_tga_to_ico(tga_file_path, ico_file_path, size=(32, 32)):
    try:
        # Open the TGA file
        image = Image.open(tga_file_path)
        
        # Resize the image to the desired size
        image = image.resize(size, Image.ANTIALIAS)
        
        # Save the image as an ICO file
        image.save(ico_file_path, format="ICO", sizes=[size])
        print "Converted {} to {} with size {}".format(tga_file_path, ico_file_path, size)
    except Exception as e:
        print "Error converting {}: {}".format(tga_file_path, str(e))

def main():
    # Get a list of all TGA files in the current directory
    tga_files = [filename for filename in os.listdir(".") if filename.lower().endswith(".tga")]

    for tga_file in tga_files:
        ico_file = tga_file.replace(".tga", ".ico")
        convert_tga_to_ico(tga_file, ico_file)

if __name__ == "__main__":
    main()
