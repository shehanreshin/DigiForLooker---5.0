#!/bin/bash
docker build -t kalisc .
docker run -d --name kalisc -v /home/reshin/Documents/docker_up_test:/data kalisc

