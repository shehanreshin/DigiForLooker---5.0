import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

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
                    metadata_array.append([path, metadata])

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
for item in metadata_array:
    print(type(item[1]))