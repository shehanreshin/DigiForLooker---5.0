from app import app
from flask import render_template, request, redirect, session, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os, re
import subprocess
import atexit, shutil
import threading
from PIL import Image
import docker
import hashlib
import multiprocessing
import ujson
import json
import mysql.connector

"""
# connect to MySQL server
mydb = mysql.connector.connect(
  host="localhost",
  user="2^j&k@8mN",
  password="hRy%3l!z#9T"
)


# create a new database
mycursor = mydb.cursor()
mycursor.execute("DROP DATABASE dfl")
mycursor.execute("CREATE DATABASE dfl")

# connect to the new database
mydb = mysql.connector.connect(
  host="localhost",
  user="2^j&k@8mN",
  password="hRy%3l!z#9T",
  database="dfl"
)

# create a new table to store file_name, md5_hash, and sha1_hash
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE current_hash (file_name VARCHAR(255), md5_hash VARCHAR(32), sha1_hash VARCHAR(40))")
"""
extracted_folders = []
path_to_file = ""
current_dir = os.path.dirname(os.path.abspath(__file__))
original_hash = {}

def uploadExtractBE(file_path):
    container_name = "kalibe"
    # Specify the path to the file you want to extract using Bulk Extractor on your local machine
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    # Specify the output directory for the extracted files within the container
    output_directory = "/output/"

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Specify the full path to the Bulk Extractor executable within the Docker container
    bulk_extractor_path = "/usr/bin/bulk_extractor"

    # Build the Docker command to run Bulk Extractor with mounted volume
    docker_command = f"docker exec {container_name} {bulk_extractor_path} -o {output_directory} /data/{os.path.basename(path_to_extract)}"

    # Run the Docker command
    subprocess.run(docker_command, shell=True)

    copy_command = f"docker cp {container_name}:{output_directory} app/static/files/downloaded/bulkextractor"
    result = subprocess.run(copy_command, shell=True)
    chmod_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/bulkextractor")
    subprocess.run(f"chmod 777 {chmod_path}", shell=True)
    if result.returncode == 0:
        return "File extracted"
    else:
        return "File extraction"

def uploadCarveScalpel(file_path):
    container_name = "kalisc"
    # Specify the path to the file you want to extract using Bulk Extractor on your local machine
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    # Specify the output directory for the extracted files within the container
    output_directory = "/output/"

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Specify the full path to the Bulk Extractor executable within the Docker container
    scalpel_path = "/usr/bin/scalpel"

    # Build the Docker command to run Bulk Extractor with mounted volume
    docker_command = f"docker exec {container_name} {scalpel_path} -c /etc/scalpel/scalpel.conf -o {output_directory} /data/{os.path.basename(path_to_extract)}"

    # Run the Docker command
    subprocess.run(docker_command, shell=True)

    copy_command = f"docker cp {container_name}:{output_directory} app/static/files/downloaded/scalpel"
    result = subprocess.run(copy_command, shell=True)
    chmod_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/scalpel")
    subprocess.run(f"chmod 777 {chmod_path}", shell=True)
    if result.returncode == 0:
        return "Files Carved"
    else:
        return "Files Carved"

def uploadCarveMR(file_path):
    container_name = "kalimr"
    # Specify the path to the file you want to extract using Bulk Extractor on your local machine
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    # Specify the output directory for the extracted files within the container
    output_directory = "/output/"

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Specify the full path to the Bulk Extractor executable within the Docker container
    scalpel_path = "/usr/bin/magicrescue"

    # Build the Docker command to run Bulk Extractor with mounted volume
    docker_command = f"docker exec {container_name} {scalpel_path} -r jpeg-exif -r jpeg-jfif -r png -d {output_directory} -M -io /data/{os.path.basename(path_to_extract)}"

    # Run the Docker command
    #subprocess.run(f"docker exec kalimr mkdir /output/{folder_name}", shell=True)
    subprocess.run(docker_command, shell=True)

    copy_command = f"docker cp {container_name}:{output_directory} app/static/files/downloaded/magicrescue"
    result = subprocess.run(copy_command, shell=True)
    chmod_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/magicrescue")
    subprocess.run(f"chmod 777 {chmod_path}", shell=True)
    if result.returncode == 0:
        return "Files Carved"
    else:
        return "Files Carved"

def getCleanFilesList(folder_path):
    files_list = os.listdir(folder_path)
    clean_files_list = []
    for file in files_list:
        try:
            if os.stat(f"{folder_path}/{file}").st_size == 0:
                pass
            else:
                clean_files_list.append(file)
        except IsADirectoryError:
            pass           
    return clean_files_list

def getFilesDict(folder_path, clean_files_list):
    files_dict = {}
    for name in clean_files_list:
        try:
            file = open(f"{folder_path}/{name}", 'r')
            f = file.readlines()
            files_dict[name] = f
        except IsADirectoryError:
            pass
    return files_dict    

# Define a function to start the containers
def start_containers():
    client = docker.from_env()
    for container_name in ["kalibe", "kalimr", "kalisc"]:
        container = client.containers.get(container_name)
        container.start()

"""
lock = threading.Lock()
class HashThread(threading.Thread):
    def __init__(self, file_path, original_hash, changed_hash):
        threading.Thread.__init__(self)
        self.file_path = file_path
        self.original_hash = original_hash
        self.changed_hash = changed_hash

    def run(self):
        with open(self.file_path, "rb") as f:
            data = f.read()
            md5_hash = hashlib.md5(data).hexdigest()
            sha1_hash = hashlib.sha1(data).hexdigest()
            file_name = os.path.basename(self.file_path)
            if file_name in self.original_hash:
                if self.original_hash[file_name]["MD5"] != md5_hash or self.original_hash[file_name]["SHA1"] != sha1_hash:
                    with lock:
                        self.changed_hash[file_name] = {"MD5": md5_hash, "SHA1": sha1_hash}
            else:
                with lock:
                    self.changed_hash[file_name] = {"MD5": md5_hash, "SHA1": sha1_hash}
"""
"""
# Define a function that reads the JSON file and stores the data in a list
def read_json_file(f, data_dict, start, end):
    f.seek(start)
    buffer = f.read(end - start)
    data = json.loads(buffer)
    for key, value in data.items():
        data_dict[key] = value

# Define a function that spawns threads to read the file in chunks
def read_large_file(f, num_threads=4):
    file_size = f.seek(0, 2)
    chunk_size = file_size // num_threads

    threads = []
    data_dict = {}
    for i in range(num_threads):
        start = i * chunk_size
        end = start + chunk_size
        if i == num_threads - 1:
            end = file_size
        t = threading.Thread(target=read_json_file, args=(f, data_dict, start, end))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return data_dict
"""
def generate_hash(folder_path):
    global mycursor
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename == ".gitkeep":
                continue
            file_path = os.path.join(dirpath, filename)
            file_paths.append(file_path)
    current_hash = {}
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            data = f.read()
            md5_hash = hashlib.md5(data).hexdigest()
            sha1_hash = hashlib.sha1(data).hexdigest()
            file_name = os.path.basename(file_path)
            current_hash[file_name] = {"MD5": md5_hash, "SHA1": sha1_hash}
            """
            sql = "INSERT INTO dfl.current_hash (file_name, md5_hash, sha1_hash) VALUES (%s, %s, %s)"
            val = (file_name, md5_hash, sha1_hash)
            mycursor.execute(sql, val)
            # commit the changes to the database
            mydb.commit()
            # print the number of rows that were inserted
            print(mycursor.rowcount, "rows were inserted.")
            """
    return current_hash

"""
def compute_hashes(folder_path, original_hash):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_paths.append(file_path)

    current_hash = {}
    changed_hash = {}
    threads = []
    for file_path in file_paths:
        thread = HashThread(file_path, original_hash, changed_hash)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    for file_path in file_paths:
        with open(file_path, "rb") as f:
            data = f.read()
            md5_hash = hashlib.md5(data).hexdigest()
            sha1_hash = hashlib.sha1(data).hexdigest()
            file_name = os.path.basename(file_path)
            current_hash[file_name] = {"MD5": md5_hash, "SHA1": sha1_hash}

    # Remove any keys from changed_hash whose values are identical in current_hash
    with lock:
        for key, value in list(changed_hash.items()):
            print(f"{value}, {current_hash[key]}")
            if value == current_hash[key]:
                del changed_hash[key]
                print("deleted")
                print(changed_hash)

    return current_hash, changed_hash
"""
"""
def update_hashes(folder_path, original_hash_path, changed_hash_path):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            file_paths.append(file_path)

    with open(original_hash_path, 'r') as f:
        original_hash = json.load(f)

    changed_hash = {}
    threads = []
    for file_path in file_paths:
        thread = HashThread(file_path, original_hash, changed_hash)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    with open(changed_hash_path, 'w') as f:
        json.dump(changed_hash, f)

    return changed_hash
"""

"""
@app.route('/dia_hash')
def diaHash():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        folder_path = os.path.join(current_dir, "static", "files")
        hash_file_path = os.path.join(current_dir, "hashes.json")

        # Try to load the original hash
        try:
            with open(hash_file_path, "r") as f:
                original_hash = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            original_hash = {}

        # If original hash does not exist, create it and save it in hashes.json file
        if not original_hash:
            current_hash, changed_hash = compute_hashes(folder_path, original_hash={})
            with open(hash_file_path, "w") as f:
                json.dump(current_hash, f)
            changed_hash = {}
        else:
            current_hash, changed_hash = compute_hashes(folder_path, original_hash)

        # Save changed hashes if there are any
        if changed_hash:
            with open(os.path.join(current_dir, "changed_hashes.json"), "w") as f:
                json.dump(changed_hash, f)

        print(changed_hash)
        return render_template(
            "dia/hash.html",    
            current_hash=current_hash,
            changed_hash=changed_hash,
            file_name=session.get("file_name"),
        )
    else:
        return render_template('dia/hash.html')
"""

@app.route('/dia_hash')
def diaHash():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        global original_hash
        folder_path = os.path.join(current_dir, "static", "files")
        current_hash = generate_hash(folder_path)
        hash_file_path = os.path.join(current_dir, "original_hashes.json")
        changed_hash = {}
        if not original_hash:
            original_hash = current_hash
        else:
            pass

        for file_name, hashes in original_hash.items():
            if file_name in current_hash:
                current_hashes = current_hash[file_name]
                if hashes != current_hashes:
                    changed_hash[file_name] = current_hashes
            else:
                changed_hash[file_name] = None

        for file_name, hashes in current_hash.items():
            if file_name not in original_hash:
                changed_hash[file_name] = hashes

        return render_template(
        "dia/hash.html",    
        current_hash=current_hash,
        changed_hash=changed_hash,
        original_hash=original_hash,
        file_name=session.get("file_name"),
        )
    else:
        return render_template('dia/hash.html')

class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dia_upload", methods=['GET', "POST"])
def diaUpload():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        file_path = "static/files/uploaded/" + file.filename
        global path_to_file
        path_to_file = file.filename
        session["file_name"] = file.filename
        # Create threads for both functions and start them
        t1 = threading.Thread(target=uploadExtractBE, args=(file_path,))
        t2 = threading.Thread(target=uploadCarveScalpel, args=(file_path,))
        t3 = threading.Thread(target=uploadCarveMR, args=(file_path,))
        t1.start()
        t2.start()
        t3.start()
        # Wait for both threads to finish before continuing
        t1.join()
        t2.join()
        t3.join()
        extracted_folders.append(file_path)
    return render_template("dia/upload.html", form=form)

@app.route("/dia_dashboard", methods=['GET', "POST"])
def diaDashboard():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        folder_path = current_dir + "/static/files/downloaded/bulkextractor/"
        clean_files_list = getCleanFilesList(folder_path)
        files_dict = getFilesDict(folder_path, clean_files_list)
        return render_template("dia/dashboard.html", folder_path=folder_path, clean_files_list=clean_files_list, files_dict=files_dict)
    else:
        return render_template("dia/dashboard.html")

@app.route('/dia_gallery')
def diaGallery():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        clean_images_list = []
        image_dir = current_dir + "/static/files/downloaded/magicrescue/"  # replace with your own image directory
        image_list = os.listdir(image_dir)
        image_list = [f for f in image_list if f.endswith('.jpg') or f.endswith('.png')]  # filter for image files
        for image in image_list:
            try:
                # Open image file
                image_path = current_dir + "/static/files/downloaded/magicrescue/" + image
                with Image.open(image_path) as img:
                    # Check if image can be displayed
                    img.verify()
            except IOError:
                # Image file cannot be opened or displayed
                print("Image file cannot be displayed.")
            except SyntaxError:
                print("Image file cannot be displayed.")
            else:
                clean_images_list.append(image)

        return render_template('dia/gallery.html', images=image_list, clean_images=clean_images_list)
    else:
        return render_template('dia/gallery.html')



@atexit.register
def deleteExtractedFolders():
    global extracted_folders
    container_name = "kalibe"
    global path_to_file
    file_name = path_to_file
    subprocess.run(f"docker exec {container_name} rm -rf /output", shell=True)    
    subprocess.run(f"sudo docker exec kalisc rm -rf /output", shell=True)
    subprocess.run(f"sudo docker exec kalimr rm -rf /output", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/bulkextractor", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/scalpel", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/magicrescue", shell=True)
    last_command = f"find {os.path.abspath(os.path.dirname(__file__))}/static/files/uploaded/ -type f ! -name '.gitkeep' -exec rm " + "{} +"
    subprocess.run(f"sudo rm -f {os.path.abspath(os.path.dirname(__file__))}/original_hashes.json", shell=True)
    subprocess.run(last_command, shell=True)
    # Delete extracted folders in local folder when flask server is stopped
    #for folder_path in extracted_folders:
        #be_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/bulkextractor")
        #shutil.rmtree(be_folder_path)
        #sc_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/scalpel")
        #shutil.rmtree(sc_folder_path)
        #mr_folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/files/downloaded/magicrescue")
        #shutil.rmtree(mr_folder_path)

@app.before_first_request
def before_first_request():
    start_containers()
    subprocess.run(f"docker exec kalibe mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalisc mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalimr mkdir /output/", shell=True)
    session['file_name'] = None
    