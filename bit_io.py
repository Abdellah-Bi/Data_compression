import sys

class BitWriter:
    """Writes arbitrary bit-width integers to a binary file."""
    def __init__(self, file_path):
        self.file = open(file_path, 'wb')
        self.buffer = 0
        self.bits_in_buffer = 0

    def write(self, code, bit_width):
        # Shift existing buffer left and add new code
        self.buffer = (self.buffer << bit_width) | code
        self.bits_in_buffer += bit_width
        
        # Pull out 8-bit chunks whenever possible
        while self.bits_in_buffer >= 8:
            self.bits_in_buffer -= 8
            byte_to_write = (self.buffer >> self.bits_in_buffer) & 0xFF
            self.file.write(bytes([byte_to_write]))
            # Keep only the remaining bits
            self.buffer &= (1 << self.bits_in_buffer) - 1

    def close(self):
        # Pad the final byte with zeros if necessary
        if self.bits_in_buffer > 0:
            self.file.write(bytes([(self.buffer << (8 - self.bits_in_buffer)) & 0xFF]))
        self.file.close()

class BitReader:
    """Reads arbitrary bit-width integers from a binary file."""
    def __init__(self, file_path):
        self.file = open(file_path, 'rb')
        self.buffer = 0
        self.bits_in_buffer = 0

    def read(self, bit_width):
        while self.bits_in_buffer < bit_width:
            byte = self.file.read(1)
            if not byte:
                return None  # Reached end of file
            self.buffer = (self.buffer << 8) | ord(byte)
            self.bits_in_buffer += 8
        
        # Extract the specific bit_width from the top of the buffer
        self.bits_in_buffer -= bit_width
        code = (self.buffer >> self.bits_in_buffer)
        self.buffer &= (1 << self.bits_in_buffer) - 1
        return code

    def close(self):
        self.file.close()