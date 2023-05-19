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
from flask import Markup

class DiskImage:
    def __init__(self, file_name):
        self.file_name = file_name
    
    @property
    def file_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'static/files/uploaded', self.file_name)
        return file_path

extracted_folders = []
path_to_file = ""
current_dir = os.path.dirname(os.path.abspath(__file__))
original_hash = {}

def uploadExtractBE(file_path):
    container_name = "kalibe"
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    output_directory = "/output/"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    bulk_extractor_path = "/usr/bin/bulk_extractor"

    docker_command = f"docker exec {container_name} {bulk_extractor_path} -o {output_directory} /data/{os.path.basename(path_to_extract)}"

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
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    output_directory = "/output/"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    scalpel_path = "/usr/bin/scalpel"
    docker_command = f"docker exec {container_name} {scalpel_path} -c /etc/scalpel/scalpel.conf -o {output_directory} /data/{os.path.basename(path_to_extract)}"
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
    path_to_extract = file_path
    folder_name = path_to_extract.split("/")
    folder_name = folder_name[-1]

    #The output directory for the extracted files within the container
    output_directory = "/output/"

    #To create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    scalpel_path = "/usr/bin/magicrescue"

    #Docker command to run Magic Rescue with mounted volume
    docker_command = f"docker exec {container_name} {scalpel_path} -r jpeg-exif -r jpeg-jfif -r png -d {output_directory} -M -io /data/{os.path.basename(path_to_extract)}"

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
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and os.stat(file_path).st_size != 0:
            clean_files_list.append(file)
    return clean_files_list

def getFilesDict(folder_path, clean_files_list):
    files_dict = {}
    for name in clean_files_list:
        try:
            file_path = f"{folder_path}/{name}"
            with open(file_path, 'rb') as file:
                content = file.read()
            files_dict[name] = content
        except IsADirectoryError:
            pass
    return files_dict    

def count_lines(content):
    line_count = content.count(b'\n')
    return line_count

app.jinja_env.filters['count_lines'] = count_lines

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


def start_containers():
    client = docker.from_env()
    for container_name in ["kalibe", "kalimr", "kalisc"]:
        container = client.containers.get(container_name)
        container.start()

def generate_hash(folder_path):
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
            
    return current_hash

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
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],
        secure_filename(file.filename)))
        file_path = "static/files/uploaded/" + file.filename
        global path_to_file
        path_to_file = file.filename
        #Creating threads for both functions and starting them
        t1 = threading.Thread(target=uploadExtractBE, args=(file_path,))
        t2 = threading.Thread(target=uploadCarveScalpel, args=(file_path,))
        t3 = threading.Thread(target=uploadCarveMR, args=(file_path,))
        t1.start()
        t2.start()
        t3.start()
        #Waiting for both threads to finish before continuing
        t1.join()
        t2.join()
        t3.join()
        extracted_folders.append(file_path)
        session["file_name"] = file.filename
    return render_template("dia/upload.html", form=form)

@app.route('/dia_gallery')
def diaGallery():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        clean_images_list = []
        image_dir = current_dir + "/static/files/downloaded/magicrescue/"
        image_list = os.listdir(image_dir)
        image_list = [f for f in image_list if f.endswith('.jpg') or f.endswith('.png')]  #filter for image files
        for image in image_list:
            try:
                #Open image file
                image_path = current_dir + "/static/files/downloaded/magicrescue/" + image
                with Image.open(image_path) as img:
                    #Check if image can be displayed
                    img.verify()
            except IOError:
                #Image file cannot be opened or displayed
                print("Image file cannot be displayed.")
            except SyntaxError:
                print("Image file cannot be displayed.")
            else:
                clean_images_list.append(image)

        return render_template('dia/gallery.html', images=image_list, clean_images=clean_images_list)
    else:
        return render_template('dia/gallery.html')

@app.route('/dia_readcard/<filename>')
def readCard(filename):
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        file_path = current_dir + "/static/files/downloaded/bulkextractor/" + filename
        try:
            file = open(file_path, 'r')
            answer = file.readlines()
        except IsADirectoryError:
            pass
        else:
            return render_template('dia/readcard.html', textContent=answer)
    else:
        return redirect(url_for('diaUpload'))

@atexit.register
def deleteExtractedFolders():
    global extracted_folders
    global path_to_file
    file_name = path_to_file
    subprocess.run(f"sudo docker exec kalibe rm -rf /output", shell=True)    
    subprocess.run(f"sudo docker exec kalisc rm -rf /output", shell=True)
    subprocess.run(f"sudo docker exec kalimr rm -rf /output", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/bulkextractor", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/scalpel", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/magicrescue", shell=True)
    last_command = f"find {os.path.abspath(os.path.dirname(__file__))}/static/files/uploaded/ -type f ! -name '.gitkeep' -exec rm " + "{} +"
    subprocess.run(f"sudo rm -f {os.path.abspath(os.path.dirname(__file__))}/original_hashes.json", shell=True)
    subprocess.run(last_command, shell=True)

@app.before_first_request
def before_first_request():
    start_containers()
    subprocess.run(f"docker exec kalibe mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalisc mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalimr mkdir /output/", shell=True)
    session['file_name'] = None
    