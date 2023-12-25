import zlib
import pickle
import os

def extract_and_decompress(file_count, index_file, dat_file):
    # Load the index
    with open(index_file, 'rb') as f:
        index_data = pickle.load(f)

    # Get file information from the index
    if file_count not in index_data:
        print("Error: File count not found in index.")
        return None

    file_info = index_data[file_count]
    offset, size = file_info['offset'], file_info['size']

    # Check if the file consists of multiple chunks
    if 'chunks_info' in file_info:
        chunks_info = file_info['chunks_info']
        decompressed_data = bytearray()
        
        with open(dat_file, 'rb') as f:
            for chunk_id in range(chunks_info['total_chunks']):
                chunk_info = chunks_info['chunks_info'][chunk_id]
                chunk_offset, chunk_size = chunk_info['offset'], chunk_info['length']
                
                f.seek(chunk_offset)
                compressed_chunk_data = f.read(chunk_size)
                # NOTE: UNCOMMENT TO ENABLE COMPRESSION/DECOMPRESSION
                # decompressed_chunk_data = zlib.decompress(compressed_chunk_d2ata)
                decompressed_data.extend(compressed_data)
    else:
        # File is not chunked, decompress the entire file
        with open(dat_file, 'rb') as f:
            f.seek(offset)
            compressed_data = f.read(size)
            decompressed_data = compressed_data # zlib.decompress(compressed_data)

    return decompressed_data

if __name__ == "__main__":
    FILE_COUNT = int(raw_input("Enter the file count number: "))
    INDEX_FILE = "app_id.index"
    DAT_FILE = "app_id.dat"
    
    data = extract_and_decompress(FILE_COUNT, INDEX_FILE, DAT_FILE)
    if data:
        output_filename = "output_file"
        with open(output_filename, 'wb') as output_file:
            output_file.write(data)
        print("Successfully extracted and decompressed the file to '{}'.".format(output_filename))
    else:
        print("Failed to extract or decompress the file.")
