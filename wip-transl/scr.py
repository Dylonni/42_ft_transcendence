import sys

def process_file(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as input_file, \
         open(output_file_path, 'w', encoding='utf-8') as output_file:
        for line in input_file:
            output_file.write(line)
            if line.strip().endswith('"'):
                # Add a new line starting with "LANG" after the current line
                output_file.write('LANG\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    process_file(input_file_path, output_file_path)