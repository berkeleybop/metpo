import csv
import sys

def create_stubs(output_file, *input_files):
    """
    Reads multiple ROBOT template files and creates a single "stubs" file
    containing only the ID, label, and TYPE for each METPO entity.
    """
    stubs = set()

    for file_path in input_files:
        try:
            with open(file_path, 'r', newline='') as infile:
                reader = csv.reader(infile, delimiter='\t')
                
                # Find the ROBOT header row (the one with 'LABEL')
                file_header = []
                while not file_header or 'LABEL' not in [h.strip() for h in file_header]:
                    file_header = next(reader)
                
                # Strip headers before finding index
                stripped_header = [h.strip() for h in file_header]
                id_index = stripped_header.index('ID')
                label_index = stripped_header.index('LABEL')
                type_index = stripped_header.index('TYPE')

                for row in reader:
                    if row and len(row) > max(id_index, label_index, type_index) and row[id_index].startswith('METPO:'):
                        stubs.add((row[id_index], row[label_index], row[type_index]))
        except FileNotFoundError:
            print(f"Warning: Input file not found: {file_path}", file=sys.stderr)
        except StopIteration:
            print(f"Warning: Could not find a valid ROBOT template header in {file_path}", file=sys.stderr)
        except ValueError:
            print(f"Warning: Could not find required columns (ID, LABEL, TYPE) in {file_header} in {file_path}", file=sys.stderr)


    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        writer.writerow(('ID', 'label', 'TYPE')) # Human-readable header
        writer.writerow(('ID', 'LABEL', 'TYPE')) # ROBOT template header
        # Sort for consistent output
        sorted_stubs = sorted(list(stubs))
        writer.writerows(sorted_stubs)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python create_stubs.py <output_file> <input_file_1> [<input_file_2> ...]")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    create_stubs(output_file, *input_files)
