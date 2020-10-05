{\rtf1\ansi\ansicpg1251\cocoartf2513
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red31\green31\blue31;\red239\green239\blue239;\red35\green38\blue42;
\red244\green244\blue244;}
{\*\expandedcolortbl;;\cssrgb\c16078\c16078\c16078;\cssrgb\c94902\c94902\c94902;\cssrgb\c18431\c20000\c21569;
\cssrgb\c96471\c96471\c96471;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf2 \cb3 \expnd0\expndtw0\kerning0
#!/bin/bash\cb1 \
\cb3 echo "Installing Python3.7" \cb1 \
\cb3 sudo apt update\cb1 \
\cb3 sudo apt install software-properities-common\cb1 \
\cb3 sudo add-apt-repository ppa:deadsnakes/ppa\cb1 \
\cb3 sudo apt install python3.7\cb1 \
\cb3 python3.7 --version \cb1 \
\cb3 echo "python3.7 is installed"\cb1 \
\cb3 echo "---------------------"\cb1 \
\cb3 echo "---------------------"\cb1 \
\cb3 echo "---------------------"\cb1 \
\cb3 echo "---------------------"\cb1 \
\cb3 echo "Installing pip3"\cb1 \
\cb3 sudo apt update\cb1 \
\cb3 sudo apt install python3-pip\cb1 \
\cb3 pip3 --version \cb1 \
\cb3 echo "pip3 installed"\
\pard\pardeftab720\partightenfactor0
\cf4 \cb5 sudo apt install chromium-chromedriver\
echo \cf2 \cb3 "chromedriver installed"
\fs26 \cf4 \cb5 \
}