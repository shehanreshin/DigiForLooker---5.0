#!/bin/bash

current_dir=$(pwd)
final_dir="$current_dir/app/static/files/uploaded/"
vol_dir="$current_dir/volatility"
docker build -t dfl_docker .
docker run -d --name kalibe -v "$final_dir:/data" -v "$vol_dir:/vol" dfl_docker
docker run -d --name kalisc -v "$final_dir:/data" -v "$vol_dir:/vol" dfl_docker
docker run -d --name kalimr -v "$final_dir:/data" -v "$vol_dir:/vol" dfl_docker