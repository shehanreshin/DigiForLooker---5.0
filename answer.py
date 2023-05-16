import subprocess

# Specify the name of the Docker container to use
container_name = "mykali4"

# Specify the path to the domain.txt file within the container
file_path = "/output/terry_usb.E01/domain.txt"

# Build the Docker command to print the contents of the file
docker_command = f"docker exec {container_name} cat {file_path}"

# Run the Docker command and capture the output
output = subprocess.check_output(docker_command, shell=True)

# Print the output to the console
print(output.decode())
