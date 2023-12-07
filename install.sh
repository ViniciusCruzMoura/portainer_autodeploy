#!/usr/bin/env bash

BASEDIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat << "EOF"
  _____ _   _  _____ _______       _      _      ______ _____  
 |_   _| \ | |/ ____|__   __|/\   | |    | |    |  ____|  __ \ 
   | | |  \| | (___    | |  /  \  | |    | |    | |__  | |__) |
   | | | . ` |\___ \   | | / /\ \ | |    | |    |  __| |  _  / 
  _| |_| |\  |____) |  | |/ ____ \| |____| |____| |____| | \ \ 
 |_____|_| \_|_____/   |_/_/    \_\______|______|______|_|  \_\
                                                                                                                              
EOF

if [ ! -d "$BASEDIR/.venv/" ]; then
	echo 'Making virtual environment'
    python3 -m venv .venv
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	echo 'Activate virtual environment'
    source .venv/bin/activate
else
	echo 'Operating system unknown. Aborting deploy'
	exit
fi

echo 'Downloading requirements'
pip install -r requirements.txt

if [ ! -f "$BASEDIR/.env" ]; then
	echo 'Creating .env'
    cp .env.example .env
fi

echo 'Installation complete. Please, configure the .env file with you credentials'
