import subprocess

def detect_encoding(file_path):
    try:
        output = subprocess.check_output(['file', '--mime', '-b', file_path])
        encoding = output.decode().split(';')[1].strip().split('=')[1]
        return encoding
    except (subprocess.CalledProcessError, IndexError):
        return None

file_path = '/home/reshin/Documents/dumps/tor.mem'
encoding = detect_encoding(file_path)
if encoding:
    print(f"The file encoding is: {encoding}")
else:
    print("Unable to detect the file encoding.")
