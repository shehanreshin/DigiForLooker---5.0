FROM kalilinux/kali-rolling

RUN apt update && apt-get update
RUN apt install -y bulk-extractor
RUN apt install -y magicrescue
RUN apt install -y scalpel
RUN apt install -y libimage-exiftool-perl
RUN apt install -y git
RUN apt install -y python3
RUN apt install -y curl

# Create volumes for /data and /app to be mounted from the host
VOLUME /data
VOLUME /vol

# Start a shell that waits for input (to keep the container running)
CMD ["bash", "-c", "tail -f /dev/null"]
