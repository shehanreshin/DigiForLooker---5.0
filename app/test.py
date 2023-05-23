import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import json
import ast

def createDictFromString(string):
    # Remove leading/trailing whitespace and surrounding curly braces
    string = string.strip().strip('{}')

    data = {}
    pairs = string.split(',\n')
    for pair in pairs:
        key_value = pair.split(': ')
        key = key_value[0].strip().strip('"')
        value = key_value[1].strip().strip('"')
        if value.startswith('[') and value.endswith(']'):
            # Handle array-like values by splitting on comma
            value = value[1:-1].split(', ')
        elif '.' in value:
            try:
                value = float(value)
            except ValueError:
                pass
        else:
            try:
                value = int(value)
            except ValueError:
                pass
        data[key] = value
    return data


def extractMetadata(docker_paths, removed_path_part):
    metadata_array = []
    container_list = ['kalisc', 'kalibe', 'kalimr']

    def extractMetadataForPath(path):
        file_name = os.path.basename(path)
        if file_name.endswith(('.jpg', '.png', '.pdf', '.docx')):
            for container in container_list:
                command = f'docker exec {container} exiftool -j {path}'
                try:
                    metadata = subprocess.check_output(command, shell=True, universal_newlines=True)
                except subprocess.CalledProcessError as e:
                    #Unsupported file type error handling
                    continue
                else:
                    local_file_path = os.path.join(removed_path_part, path.replace('/data/', ''))
                    formatted_metadata = metadata.replace("[{", '')
                    formatted_metadata = formatted_metadata.replace("}]", '')
                    data = createDictFromString(formatted_metadata)
                    metadata_array.append([path, data])

    with ThreadPoolExecutor() as executor:
        executor.map(extractMetadataForPath, docker_paths)

    return metadata_array

project_dir = os.path.dirname(os.path.abspath(__file__))
def getAllFiles(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_list.append(file_path)
    return file_list



folder_path = f"{project_dir}/static/files/downloaded/"
docker_path = f"/data/"
removed_path_part = f"{project_dir}/static/files/"


files = getAllFiles(folder_path)
docker_paths = []

for file_path in files:
    docker_file_path = docker_path + file_path.replace(removed_path_part, '')
    docker_paths.append(docker_file_path)

metadata_array = extractMetadata(docker_paths, removed_path_part)
item = metadata_array[0]
print(type(item))
data = item[1]
print(type(data))
print(f'FileName: {data.get("FileName")}')
print(f'Compression: {data.get("Compression")}')
print(f'PixelUnits: {data.get("PixelUnits")}')