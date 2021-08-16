#!/bin/bash

# Install the Python requirements
pip install -r requirements.txt

# 
touch keys.json
echo "" >> keys.json

echo "{" >> keys.json
echo "    \"tcgplayer\": {" >> keys.json
echo "        \"public\": \"<your public key here>\"," >> keys.json
echo "        \"private\": \"<your private key here>\"," >> keys.json
echo "        \"user_agent_header\": \"<your project name here>\"" >> keys.json
echo "    }" >> keys.json
echo "}" >> keys.json

# Make the tokens directory
mkdir tokens
