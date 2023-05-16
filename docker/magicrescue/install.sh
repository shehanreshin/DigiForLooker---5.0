#!/bin/bash
docker build -t kalimr .
docker run -d --name kalimr -v /home/reshin/Documents/docker_up_test:/data kalimr
