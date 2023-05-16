import os
import subprocess

subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/bulkextractor", shell=True)

#docker exec kalimr /usr/bin/magicrescue -r jpeg-exif -r jpeg-jfif -r png -d /output/Windows -M -io /data/