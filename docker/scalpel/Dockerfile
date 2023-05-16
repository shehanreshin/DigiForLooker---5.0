# Use the kalilinux/kali-rolling base image
FROM kalilinux/kali-rolling

# Install bulk-extractor
RUN apt update && apt install -y scalpel

# Create the output directory
RUN mkdir /output

# Set the working directory to /output
WORKDIR /output

# Create a volume for /data to be mounted from the host
VOLUME /data

# Start a shell that waits for input (to keep the container running)
CMD ["bash", "-c", "tail -f /dev/null"]

