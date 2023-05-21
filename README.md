# DigiForLooker-5.0

PUSL3119 Project 5.0. This contains the source code of the project updated up until the Final Viva date (23rd May 2023)

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

Now the containers needs to be created. Type in the following command and press enter

```
./install.sh
```

This will take some time. Make sure you have a good stable internet connection to minimize the
risk of errors. Once the process is done, you can enter

```
docker ps -a
```

If all 3 of your containers are running, you are good to go. If not, you might need to delete the
containers and retry the installation process. Now, go to app/views.py and paste the OpenAI API key. You can generate this from https://platform.openai.com/account/api-keys. Save it and then you can enter the command

```
python3 run.py
```

to start up the Flask server. If there are any issues, the server will most likely not start. If it starts,
congratulations! The installation process is done. You can visit the link highlighted in the terminal
to access DigiForLooker. It is highly recommended that you stop and start the Flask server everytime you want to upload a file.
