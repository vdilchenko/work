#!/bin/bash
echo "Installing Python3.8" 
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3
python3 --version 
echo "python3 is installed"
echo "---------------------"
echo "---------------------"
echo "---------------------"
echo "---------------------"
echo "Installing pip3"
sudo apt update
sudo apt install python3-pip
pip3 --version 
echo "pip3 installed"

