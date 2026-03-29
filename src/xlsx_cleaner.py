import openpyxl
import sys

def open_thing(path, sheet):
    try:
        wb = openpyxl.load_workbook(path)
        ws = wb[sheet]
        return wb, ws
    except err:
        return None, f"Failed to open {path}"

def copy_file(src_path, dst_path):
    try:
        with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
            dst.write(src.read())
        return True
    except:
        return False

def to_degrees(number):
    def sanitize_num(number):
        while (abs(number) > 600):
            number /= 10
        return number

    if (number == None):
        return None

    if (isinstance(number, str)):
        # Make sure strings are always negative
        if (number[0] != "-"):
            return f"-{number}"
        return number

    number = sanitize_num(number)
    sign = "-" # Always asume negative coordinates
    number = abs(number)
    deg = int(number)
    rem_deg = number - deg
    mins = int(rem_deg * 60)
    rem_mins = (rem_deg * 60) - mins
    secs = rem_mins * 60
    secs_fmt = f"{secs:.2f}"
    secs_comma = secs_fmt.replace('.', ',')
    return f"{sign}{deg}°{mins}´{secs_comma}\""

def process_file(path, sheet):
    if (not copy_file(path, f"{path}.bak")):
        return False, f"Failed to copy file {path}"
    wb, ws = open_thing(path, sheet)
    if (wb == None):
        return False, ws
    for row in ws.iter_rows(min_row=5, min_col=4, max_col=5):
        lat, lon = to_degrees(row[0].value), to_degrees(row[1].value)
        row[0].value = lat
        row[1].value = lon
    wb.save(path)
    return True, None

if (len(sys.argv) < 2):
    print("ERROR: Por favor, ingresa la ruta a un archivo como primer argumento")
    sys.exit(1)
file_path = sys.argv[1]
print(f"- Procesando archivo \"{file_path}\"")

file_sheet = "Hoja1"
if (len(sys.argv) >= 3):
    file_sheet = sys.argv[2]
    print(f"- Parseando hoja \"{file_sheet}\"")
else:
    print("- Nombre de hoja no provisto, usando \"Hoja1\"")

succ, err = process_file(file_path, file_sheet)
if (not succ):
    print(f"ERROR: {err}")
    sys.exit(1)
print(f"- Copia de seguridad guardada en {file_path}.bak")
print("Listo!!!")
