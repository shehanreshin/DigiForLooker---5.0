import subprocess
import os

# Specify the name of the Docker container to use
container_name = "kalibe"

# Specify the path to the file you want to extract using Bulk Extractor on your local machine
path_to_extract = "app/static/files/uploaded/Windows_RAM.mem"
folder_name = path_to_extract.split("/")
folder_name = folder_name[-1]

# Specify the output directory for the extracted files within the container
output_directory = "/output/" + folder_name

# Create the output directory if it does not exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Specify the full path to the Bulk Extractor executable within the Docker container
bulk_extractor_path = "/usr/bin/bulk_extractor"

# Build the Docker command to run Bulk Extractor with mounted volume
docker_command = f"docker exec {container_name} {bulk_extractor_path} -o {output_directory} /data/{os.path.basename(path_to_extract)}"

# Run the Docker command
subprocess.run(docker_command, shell=True)

copy_command = f"docker cp {container_name}:{output_directory} app/static/files/downloaded/"
subprocess.run(copy_command, shell=True)
