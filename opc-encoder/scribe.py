# scribe.py

def read_file(path:str) -> list:
    try:
        # Read file
        with open(path, 'r') as old_file:
            old_lines = old_file.readlines()
        return old_lines
    except Exception as e:
        print(f"Error occured while reading file: {e}")
        traceback.print_exc()
        return []

def write_new_lines(path:str, new_lines: list):
    # Write new lines into file if there are more than 5 lines
    if len(new_lines) > 5:
        with open(path, 'w') as new_file:
            new_file.writelines(new_lines)
    else:
        print(f"[Encoding Remover][Warning] Refusing to overwrite - too few lines: {path}")