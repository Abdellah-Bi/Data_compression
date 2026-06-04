import json
import os
from bit_io import BitWriter

MAX_CODE_COUNT = 4096
ASCII_CODE_COUNT = 256

def load_seed_dictionary(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)
    
    # Initialize dictionary with single-byte symbols.
    dictionary = {bytes([i]): i for i in range(ASCII_CODE_COUNT)}
    
    if len(patterns) > MAX_CODE_COUNT - ASCII_CODE_COUNT:
        raise ValueError("Seed dictionary is too large for the 12-bit code space.")

    # Add mined patterns immediately after the ASCII range.
    for idx, pattern in enumerate(patterns, start=ASCII_CODE_COUNT):
        dictionary[pattern.encode("utf-8")] = idx
        
    return dictionary

def compress(input_file, output_file, seed_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    dictionary = load_seed_dictionary(seed_file)
    next_code = len(dictionary)
    bit_width = 12  # Fixed width for stability
    
    writer = BitWriter(output_file)
    with open(input_file, 'rb') as f:
        data = f.read()

    current_string = b""
    for byte_value in data:
        char = bytes([byte_value])
        combined = current_string + char
        if combined in dictionary:
            current_string = combined
        else:
            # Write the code for current_string
            writer.write(dictionary[current_string], bit_width)
            
            # Add to dictionary if space allows
            if next_code < MAX_CODE_COUNT:
                dictionary[combined] = next_code
                next_code += 1
            
            current_string = char

    if current_string:
        writer.write(dictionary[current_string], bit_width)
    
    writer.close()
    print(f"Compression complete. Final dictionary size: {next_code}")
    print(f"Output saved to: {output_file}")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Ensure the path matches your 'requests' folder structure
    input_path = "requests/setup.py" 
    compress(input_path, "setup.lzw", "seed_dictionary.json")