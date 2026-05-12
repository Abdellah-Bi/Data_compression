import json
from bit_io import BitReader

def load_seed_dictionary_for_decoder(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)
    
    # Initialize dictionary with ASCII (0-255)
    # Decoder mapping: Index -> String
    dictionary = {i: chr(i) for i in range(256)}
    
    # Add our mined patterns (256-1023)
    for idx, pattern in enumerate(patterns, start=256):
        dictionary[idx] = pattern
        
    return dictionary

def decompress(input_file, output_file, seed_file):
    dictionary = load_seed_dictionary_for_decoder(seed_file)
    next_code = 1024
    bit_width = 12 # Must match encoder exactly
    
    reader = BitReader(input_file)
    
    code = reader.read(bit_width)
    if code is None:
        reader.close()
        return

    current_string = dictionary[code]
    result = [current_string]

    while True:
        code = reader.read(bit_width)
        if code is None:
            break
            
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            entry = current_string + current_string[0]
        else:
            raise ValueError(f"Sync Error: Code {code} not in dict. Dict size: {next_code}")

        result.append(entry)

        if next_code < 4096:
            dictionary[next_code] = current_string + entry[0]
            next_code += 1
                
        current_string = entry

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(result))
    
    reader.close()
    print(f"Decompression complete. Reconstructed: {output_file}")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    decompress("setup.lzw", "restored_setup.py", "seed_dictionary.json")