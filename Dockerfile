# Use the kalilinux/kali-rolling base image
FROM kalilinux/kali-rolling

# Install bulk-extractor
RUN apt update && apt install -y bulk-extractor
RUN apt install -y magicrescue
RUN apt install -y scalpel

# Create a volume for /data to be mounted from the host
VOLUME /data

# Start a shell that waits for input (to keep the container running)
CMD ["bash", "-c", "tail -f /dev/null"]