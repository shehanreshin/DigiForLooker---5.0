from app import app
from flask import render_template, request, redirect, session, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os, re, subprocess, atexit, shutil, threading, docker, hashlib, multiprocessing
import ujson, json, requests, openai, time, glob, imagehash, concurrent.futures, whois
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
from flask import Markup

#Insert your Chat GPT API here
openai.api_key = 'addyourapikeyhere'
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

#-----------------------------------------------------------------Memory Dump Analysis-----------------------------------------------------------------

#Below is the list of the banners that can be used as parameters for Volatility
#Each of the banners extracts a data from the memory dump that fits a specific criteria or context
#Feel free to remove banners from this list as you please. The lesser the banners, the faster the execution time
#vol_banners = ["configwriter.ConfigWriter","frameworkinfo.FrameworkInfo","isfinfo.IsfInfo","layerwriter.LayerWriter","linux.bash.Bash","linux.check_afinfo.Check_afinfo","linux.check_creds.Check_creds","linux.check_idt.Check_idt","linux.check_modules.Check_modules","linux.check_syscall.Check_syscall","linux.elfs.Elfs","linux.envars.Envars","linux.iomem.IOMem","linux.keyboard_notifiers.Keyboard_notifiers","linux.kmsg.Kmsg","linux.lsmod.Lsmod","linux.lsof.Lsof","linux.malfind.Malfind","linux.mountinfo.MountInfo","linux.proc.Maps","linux.psaux.PsAux","linux.pslist.PsList","linux.psscan.PsScan","linux.pstree.PsTree","linux.sockstat.Sockstat","linux.tty_check.tty_check","mac.bash.Bash","mac.check_syscall.Check_syscall","mac.check_sysctl.Check_sysctl","mac.check_trap_table.Check_trap_table","mac.ifconfig.Ifconfig","mac.kauth_listeners.Kauth_listeners","mac.kauth_scopes.Kauth_scopes","mac.kevents.Kevents","mac.list_files.List_Files","mac.lsmod.Lsmod","mac.lsof.Lsof","mac.malfind.Malfind","mac.mount.Mount","mac.netstat.Netstat","mac.proc_maps.Maps","mac.psaux.Psaux","mac.pslist.PsList","mac.pstree.PsTree","mac.socket_filters.Socket_filters","mac.timers.Timers","mac.trustedbsd.Trustedbsd","mac.vfsevents.VFSevents","timeliner.Timeliner","windows.bigpools.BigPools","windows.callbacks.Callbacks","windows.cmdline.CmdLine","windows.crashinfo.Crashinfo","windows.devicetree.DeviceTree","windows.dlllist.DllList","windows.driverirp.DriverIrp","windows.drivermodule.DriverModule","windows.driverscan.DriverScan","windows.dumpfiles.DumpFiles","windows.envars.Envars","windows.filescan.FileScan","windows.getservicesids.GetServiceSIDs","windows.getsids.GetSIDs","windows.handles.Handles","windows.info.Info","windows.joblinks.JobLinks","windows.ldrmodules.LdrModules","windows.malfind.Malfind","windows.mbrscan.MBRScan","windows.memmap.Memmap","windows.modscan.ModScan","windows.modules.Modules","windows.mutantscan.MutantScan","windows.poolscanner.PoolScanner","windows.privileges.Privs","windows.pslist.PsList","windows.psscan.PsScan","windows.pstree.PsTree","windows.registry.certificates.Certificates","windows.registry.hivelist.HiveList","windows.registry.hivescan.HiveScan","windows.registry.printkey.PrintKey","windows.registry.userassist.UserAssist","windows.sessions.Sessions","windows.ssdt.SSDT","windows.statistics.Statistics","windows.strings.Strings","windows.symlinkscan.SymlinkScan","windows.vadinfo.VadInfo","windows.vadwalk.VadWalk","windows.virtmap.VirtMap"]
vol_banners = ["windows.registry.printkey","windows.registry.userassist","windows.sessions","windows.ssdt","windows.statistics","windows.symlinkscan","windows.vadinfo","windows.vadwalk","windows.virtmap","windows.dlllist"]

def uploadVol(file_path):
    global current_dir
    global vol_banners
    file_path = file_path.split("/")
    file_name = file_path[-1]
    for banner in vol_banners:
        docker_command = f"sudo docker exec kalisc python3 /vol/vol.py -f /data/{file_name} {banner} > {current_dir}/static/files/downloaded/volatility/{banner}.txt"
        subprocess.run(docker_command, shell=True)

def checkSingleLine(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read().strip()
    single_line = "Volatility 3 Framework 2.4.1"
    return file_content == single_line

def checkUnsatisfiedRequirementPlugins(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read().strip()
    return "Unsatisfied requirement plugins" in file_content

def getCleanVolList():
    global current_dir
    folder_path = f"{current_dir}/static/files/downloaded/volatility/"
    files_list = os.listdir(folder_path)
    clean_files_list = []
    for file in files_list:
        if file == ".gitkeep":
            continue
        file_path = os.path.join(folder_path, file)
        if checkSingleLine(file_path) != True and checkUnsatisfiedRequirementPlugins(file_path) != True:
            clean_files_list.append(file)
    return clean_files_list

def getVolDict(clean_vol_list):
    global current_dir
    folder_path = f"{current_dir}/static/files/downloaded/volatility/"
    files_dict = {}
    for name in clean_vol_list:
        try:
            file_path = f"{folder_path}/{name}"
            with open(file_path, 'rb') as file:
                content = file.read()
            files_dict[name] = content
        except IsADirectoryError:
            pass
    return files_dict

def getVolData(location):
    data = []
    with open(location, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line == "Volatility 3 Framework 2.4.1" or not line:
                continue
            elements = line.split('\t') #Splitting with tab
            data.append(elements)
    return data

def convertToHTMLTable(data):

    html = '<table class="current-hash-table">\n'
    html += '<thead><tr>'
    
    headers = data[0]
    for header in headers:
        html += '<th>' + header + '</th>'
    html += '</tr></thead>\n<tbody>'
    
    for row in data[1:]:
        html += '<tr>'
        for i in range(len(row)):
            html += '<td>' + row[i] + '</td>'
        for _ in range(len(row), len(data[0])):
            html += '<td></td>'
        html += '</tr>\n'
    
    html += '</tbody></table>'
    return html

@app.route("/mda_dashboard", methods=['GET', "POST"])
def mdaDashboard():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        clean_vol_list = getCleanVolList()
        vol_dict = getVolDict(clean_vol_list)
        return render_template("mda/dashboard.html", clean_vol_list=clean_vol_list, vol_dict=vol_dict)
    else:
        return redirect(url_for('diaUpload'))

@app.route('/mda_readcard/<filename>')
def readMDACard(filename):
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        if filename == "windows.dlllist.txt":
            return redirect(url_for('mdaDLLList'))
        html_location = f"{os.path.dirname(os.path.abspath(__file__))}/templates/mda/data/{filename[:-4]}.html"
        data_location = f"{current_dir}/static/files/downloaded/volatility/{filename}"
        data = getVolData(data_location)
        html_table = convertToHTMLTable(data)
        with open(html_location, 'w') as file:
            file.write(html_table)
        
        return render_template('mda/readcard.html', filename=filename)
    else:
        return redirect(url_for('diaUpload'))

@app.route("/mda_dlllist")
def mdaDLLList():
    if 'file_name' in session and session['file_name'] is not None:
        data = []
        global current_dir
        location = current_dir + "/static/files/downloaded/volatility/windows.dlllist.txt"
        with open(location, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line == "Volatility 3 Framework 2.4.1":
                    continue
                if line and not line.startswith('PID'):
                    elements = line.split('\t')  #Splitting with tab
                    data.append(elements)

        #Generate the table
        html = '<table class="current-hash-table">\n'
        html += '<thead><tr><th>PID</th><th>Process</th><th>Base</th><th>Size</th><th>Name</th><th>Path</th><th>LoadTime</th><th>File</th><th>Output</th></tr></thead>\n<tbody>'
        for entry in data:
            html += '<tr>'
            for i in range(9):
                if i < len(entry):
                    html += '<td>' + entry[i] + '</td>'
                else:
                    html += '<td></td>'  #Add an empty cell for missing values
            html += '</tr>\n'
        html += '</tbody></table>'

        location = f"{os.path.dirname(os.path.abspath(__file__))}/templates/mda/data/dlllist_data.html"
        with open(location, 'w') as file:
            file.write(html)
        return render_template("mda/dlllist.html")
    else:
        return redirect(url_for('diaUpload'))

@app.route('/get-description/<dll_name>')
def get_description(dll_name):

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Generate a short description of (maximum 150 words) for the DLL {dll_name}",
        temperature=0,
        max_tokens=60,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    description = response.choices[0].text.strip()
    return jsonify({'description': description})

#------------------------------x--------------x---------------x------Memory Dump Analysis--------x-------------------x-----------------x---------------------


#-----------------------------------------------------------------Disk Image Analysis-----------------------------------------------------------------
scalpel_done = threading.Event()

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
    scalpel_done.set()

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
        return redirect(url_for('diaUpload'))


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
        return redirect(url_for('diaUpload'))

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
        cleanseProject()
        initializeProject()
        time.sleep(5)  # Wait for 5 seconds
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],
        secure_filename(file.filename)))
        file_path = "static/files/uploaded/" + file.filename
        global path_to_file
        path_to_file = file.filename

        #Creating threads for all the functions and starting them
        t1 = threading.Thread(target=uploadExtractBE, args=(file_path,))
        t2 = threading.Thread(target=uploadCarveScalpel, args=(file_path,))
        t3 = threading.Thread(target=uploadCarveMR, args=(file_path,))
        t4 = threading.Thread(target=uploadVol, args=(file_path,))

        t1.start()
        t2.start()
        t3.start()

        #Waiting for uploadCarveScalpel to finish before continuing
        scalpel_done.wait()

        #Starting uploadVol after uploadCarveScalpel finishes
        t4.start()

        t1.join()
        t2.join()
        t3.join()
        t4.join()

        extracted_folders.append(file_path)
        session["file_name"] = file.filename
    return render_template("dia/upload.html", form=form)

@app.route('/dia_gallery')
def diaGallery():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        image_dir = current_dir + "/static/files/downloaded/"
        clean_images_list = getCleanImages(getAllImages(image_dir))
        return render_template('dia/gallery.html', clean_images=clean_images_list, project_path=current_dir)
    else:
        return redirect(url_for('diaUpload'))

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

@app.route('/dia_analytics')
def diaAnalytics():
    if 'file_name' in session and session['file_name'] is not None:
        return render_template('dia/analytics.html')
    else:
        return redirect(url_for('diaUpload'))

def comparePHash(folder1, folder2):
    image_files1 = glob.glob(os.path.join(folder1, '**', '*'), recursive=True)
    image_files2 = os.listdir(folder2)

    similarity_array = []

    for file1 in image_files1:
        if os.path.isfile(file1):
            try:
                image1 = Image.open(file1)
                hash1 = imagehash.average_hash(image1)
            except (Image.UnidentifiedImageError, OSError):
                continue
            else:
                for file2 in image_files2:
                    try:
                        image2 = Image.open(os.path.join(folder2, file2))
                        hash2 = imagehash.average_hash(image2)
                    except (Image.UnidentifiedImageError, OSError):
                        continue
                    else:
                        similarity = round((1 - (hash1 - hash2) / len(hash1.hash) ** 2)*100)
                        file2_path = f"{os.path.join(folder2, file2)}"
                        if similarity >= 90:
                            similarity_array.append([file1, file2_path, similarity])


    return similarity_array

@app.route('/dia_phash')
def diaPHash():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        project_path = current_dir
        folder_path1 = f"{current_dir}/static/files/downloaded/scalpel/"
        folder_path2 = f"{current_dir}/static/files/downloaded/magicrescue/"
        similarity_array = comparePHash(folder_path1, folder_path2)
        return render_template('dia/phash.html', similarity_array=similarity_array, project_path=project_path)
    else:
        return redirect(url_for('diaUpload'))

def compareSSIM(folder1, folder2):
    image_files1 = [f for f in glob.glob(os.path.join(folder1, '**', '*'), recursive=True) if os.path.isfile(f)]
    image_files2 = [f for f in glob.glob(os.path.join(folder2, '**', '*'), recursive=True) if os.path.isfile(f)]

    similarity_array = []

    def compare_images(file1, file2):
        try:
            image1 = Image.open(file1)
        except (Image.UnidentifiedImageError, OSError):
            return
        else:
            try:
                image2 = Image.open(file2)
            except (Image.UnidentifiedImageError, OSError):
                return
            else:
                try:
                    #Resizing the image pre-processing
                    width, height = image1.size
                    image2 = image2.resize((width, height))
                except (ValueError, OSError):
                    return
                else:
                    try:
                        #Convert to grayscale for the calculations
                        image1_gray = image1.convert("L")
                        image2_gray = image2.convert("L")
                    except (ValueError, OSError):
                        return
                    else:
                        similarity = ssim(np.array(image1_gray), np.array(image2_gray)) * 100

                        if similarity >= 90:
                            similarity_array.append([file1, file2, similarity])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for file1 in image_files1:
            for file2 in image_files2:
                futures.append(executor.submit(compare_images, file1, file2))

        for future in concurrent.futures.as_completed(futures):
            future.result()

    return similarity_array

@app.route('/dia_ssim')
def diaSSIM():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        project_path = current_dir
        folder_path1 = f"{current_dir}/static/files/downloaded/scalpel/"
        folder_path2 = f"{current_dir}/static/files/downloaded/magicrescue/"
        similarity_array = compareSSIM(folder_path1, folder_path2)
        return render_template('dia/phash.html', similarity_array=similarity_array, project_path=project_path)
    else:
        return redirect(url_for('diaUpload'))

def getAllImages(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']  #If you have more image file extensions you want to include, add them into this
    
    image_list = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                image_list.append(os.path.join(root, file))
    
    return image_list

def getCleanImages(image_list):
    clean_images_list = []
    for image in image_list:
            try:
                with Image.open(image) as img:
                    #Check if image can be displayed
                    img.verify()
            except IOError:
                #Image file cannot be opened or displayed
                continue
            except SyntaxError:
                continue
            else:
                clean_images_list.append(image)

    return clean_images_list

@app.route('/aperi', methods=['POST'])
def aperi_solve():
    image_path = request.form.get('image_path')
    urls = getAperiSolveURL(image_path)
    return jsonify(urls)

def getAperiSolveURL(image_path):
    result = subprocess.run(f"aperisolve {image_path}", capture_output=True, text=True, shell=True)
    output = str(result)
    pattern = r"https?://www\.aperisolve\.com/\S+"
    urls = re.findall(pattern, output)
    url = urls[0]
    return url[:-5]

@app.route('/dia_steg')
def diaSteg():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        image_dir = current_dir + "/static/files/downloaded/"
        clean_images_list = getCleanImages(getAllImages(image_dir))
        return render_template('dia/steg.html', clean_images=clean_images_list, project_path=current_dir)
    else:
        return redirect(url_for('diaUpload'))

def createDictFromString(string):
    string = string.strip().strip('{}')

    data = {}
    pairs = string.split(',\n')
    for pair in pairs:
        key_value = pair.split(': ')
        key = key_value[0].strip().strip('"')
        value = key_value[1].strip().strip('"')
        if value.startswith('[') and value.endswith(']'):
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(extractMetadataForPath, docker_paths)

    return metadata_array

def getAllFiles(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_list.append(file_path)
    return file_list

@app.route('/dia_metadata')
def diaMetadata():
    if 'file_name' in session and session['file_name'] is not None:
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = f"{project_dir}/static/files/downloaded/"
        docker_path = f"/data/"
        removed_path_part = f"{project_dir}/static/files/"

        subprocess.run(f"sudo cp -r {folder_path} {project_dir}/static/files/uploaded/", shell=True)
        time.sleep(5)

        files = getAllFiles(folder_path)
        docker_paths = []

        for file_path in files:
            docker_file_path = docker_path + file_path.replace(removed_path_part, '')
            docker_paths.append(docker_file_path)

        metadata_array = extractMetadata(docker_paths, removed_path_part)
        return render_template('dia/metadata.html', metadata_array=metadata_array, project_path=project_dir)
    else:
        return redirect(url_for('diaUpload'))

def extractIPInfo(filename):
    ip_info = []
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('n='):
                parts = line.split('\t')
                ip_address = parts[1]
                output = whois.whois(ip_address)
                ip_info.append([ip_address, str(output)])
    
    return ip_info

@app.route('/dia_ipinfo')
def diaIPInfo():
    if 'file_name' in session and session['file_name'] is not None:
        global current_dir
        filename = f'{current_dir}/static/files/downloaded/bulkextractor/ip_histogram.txt'
        ip_info = extractIPInfo(filename)
        return render_template('dia/ipinfo.html', ip_info=ip_info)
    else:
        return redirect(url_for('diaUpload'))

#---------------------------------x---------------------x-----------Disk Image Analysis----------x---------------------x----------------------------------


#-----------------------------------------------------------------Project Folder & Server Maintainence-----------------------------------------------------------------

def initializeProject():
    subprocess.run(f"docker exec kalibe mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalisc mkdir /output/", shell=True)
    subprocess.run(f"docker exec kalimr mkdir /output/", shell=True)

def cleanseProject():
    global extracted_folders
    global path_to_file
    file_name = path_to_file
    subprocess.run(f"sudo docker exec kalibe rm -rf /output", shell=True)    
    subprocess.run(f"sudo docker exec kalisc rm -rf /output", shell=True)
    subprocess.run(f"sudo docker exec kalimr rm -rf /output", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/bulkextractor", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/scalpel", shell=True)
    subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/magicrescue", shell=True)
    if os.path.exists(f"{os.path.abspath(os.path.dirname(__file__))}/static/files/uploaded/downloaded/"):
        subprocess.run(f"sudo rm -rf {os.path.abspath(os.path.dirname(__file__))}/static/files/uploaded/downloaded", shell=True)
    subprocess.run(f"find {os.path.abspath(os.path.dirname(__file__))}/static/files/uploaded/ -type f ! -name '.gitkeep' -exec rm " + "{} +" , shell=True)
    subprocess.run(f"find {os.path.abspath(os.path.dirname(__file__))}/static/files/downloaded/volatility/ -type f ! -name '.gitkeep' -exec rm " + "{} +" , shell=True)
    subprocess.run(f"find {os.path.abspath(os.path.dirname(__file__))}/templates/mda/data/ -type f ! -name '.gitkeep' -exec rm " + "{} +" , shell=True)

@atexit.register
def deleteExtractedFolders():
    cleanseProject()

@app.before_first_request
def before_first_request():
    start_containers()
    initializeProject()
    session['file_name'] = None

#---------------------------------x---------------------x-----------Project Folder & Server Maintainence----------x---------------------x----------------------------------