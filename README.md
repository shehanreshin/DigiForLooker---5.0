# DigiForLooker-5.0

PUSL3119 Project 5.0. This contains the source code of the project updated up until the Final Viva date (23rd May 2023). Digital Forensic Looker is a GUI-Based toolkit for Linux distributions that can be used to perform disk image analysis and memory dump analysis. This web application is specifically designed to cater to amateur digital forensic investigators and students in the digital forensic field. It offers a comprehensive collection of digital forensic tools and OSINT tools that work together, resulting in more accurate results by comparing the outputs of each tool. The toolkit aims to increase efficiency in performing these 2 tasks, and also includes a specially designed color palette to reduce eye strain.

# Installation

Clone the git repo by typing the following in the terminal,

```
git clone https://github.com/shehanreshin/DigiForLooker---5.0.git
```

Next you need to install Docker. Depending on your Linux distribution, the command can change.
In Ubuntu the command is,

```
sudo apt update && apt install docker
```

In Fedora the command is,

```
sudo dnf update && dnf install docker-ce
```

Please refer to the official documentation to find out the installation process of Docker for your OS.
Once Docker is installed, install python3 and pip3

```
sudo apt install python3 python3-pip
```

Once again, this can differ from distribution to distribution because most OS have different package
managers, so make sure to refer the official documentation if you ever come across an issue. Once
both those packages are done installing, open a terminal in the cloned Github repository. Type in the
command

```
pip3 install -r requirements.txt
```

This will download all the python libraries required for the project. Once that is done, switch to the
root account for root permissions using

```
sudo su
```

Now the containers needs to be created. But before that, go to the scalpel.conf file and remove the '#' symbol (uncomment) from the line of any other type of data you want to extract using Scalpel. By default, it will extract JPG, PNG, DBX, OST, PST and TXT. After you are done, type in the following command and press enter

```
./install.sh
```

This will take some time. Make sure you have a good stable internet connection to minimize the
risk of errors. Once the process is done, you can enter

```
docker ps -a
```

If all 3 of your containers are running, you are good to go. If not, you might need to delete the
containers and retry the installation process. Now you need to install Aperi'Solve. To do this you need to use curl. If curl is not installed, refer to the curl documentation on how to install it on your OS. You can install Curl on Debian based distributions such as Ubuntu using

```
sudo apt install curl
```

On Arch Using

```
sudo pacman -S curl
```

and on Fedora using

```
sudo yum install curl
```

Once that is done, you can enter the command

```
sudo sh -c "$(curl -fs https://www.aperisolve.com/install.sh)"
```

to install Aperi'Solve. Now, go to app/views.py and paste the OpenAI API key. You can generate this from https://platform.openai.com/account/api-keys. You can also add or remove banners that you want to run in volatility by editing the vol_banners list. Once you're done, save it and then you can enter the command

```
python3 run.py
```

to start up the Flask server. If there are any issues, the server will most likely not start. If it starts,
congratulations! The installation process is done. You can visit the link highlighted in the terminal
to access DigiForLooker. It is highly recommended that you stop and start the Flask server everytime you want to upload a file. You can get some sample files for testing from the following link: https://liveplymouthac-my.sharepoint.com/:f:/g/personal/10673843_students_plymouth_ac_uk/EgDVTW3fb29PhovY-c4nEVgBxxiilM80bWI3d7es4BuAFg?e=thK140

If you run into any issues during the installation process and cannot find a solution, feel free to contact me. I'll do my best to be of assistance.
