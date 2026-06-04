import json
from bit_io import BitReader

MAX_CODE_COUNT = 4096
ASCII_CODE_COUNT = 256

def load_seed_dictionary_for_decoder(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)
    
    dictionary = {i: bytes([i]) for i in range(ASCII_CODE_COUNT)}

    if len(patterns) > MAX_CODE_COUNT - ASCII_CODE_COUNT:
        raise ValueError("Seed dictionary is too large for the 12-bit code space.")
    
    for idx, pattern in enumerate(patterns, start=ASCII_CODE_COUNT):
        dictionary[idx] = pattern.encode("utf-8")
        
    return dictionary

def decompress(input_file, output_file, seed_file):
    dictionary = load_seed_dictionary_for_decoder(seed_file)
    next_code = len(dictionary)
    bit_width = 12
    
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
            entry = current_string + current_string[:1]
        else:
            raise ValueError(f"Sync Error: Code {code} not in dict. Dict size: {next_code}")

        result.append(entry)

        if next_code < MAX_CODE_COUNT:
            dictionary[next_code] = current_string + entry[:1]
            next_code += 1
                
        current_string = entry

    with open(output_file, 'wb') as f:
        f.write(b"".join(result))
    
    reader.close()
    print(f"Decompression complete. Reconstructed: {output_file}")

if __name__ == "__main__":
    decompress("setup.lzw", "restored_setup.py", "seed_dictionary.json")