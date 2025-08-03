#!/bin/bash

set -e

npm uninstall -g @angular/cli
sudo apt remove --purge nodejs npm -y
sudo apt autoremove -y
rm -rf /etc/sudo apt/sources.list.d/nodesource.list
rm -rf /usr/local/lib/node_modules
rm -rf ~/.npm ~/.nvm ~/.node-gyp
rm -rf /usr/local/bin/node /usr/local/bin/npm /usr/local/bin/npx

sudo apt update -y
sudo apt upgrade -y

sudo apt install -y curl software-properties-common

curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

sudo apt install -y nodejs

npm install -g @angular/cli@20
