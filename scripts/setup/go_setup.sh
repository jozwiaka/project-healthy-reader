#!/bin/bash

ARCH="linux-amd64"
LATEST_VERSION=$(curl -s https://go.dev/VERSION?m=text | awk '/^go/ { print $1; exit }')
GO_TARBALL="${LATEST_VERSION}.${ARCH}.tar.gz"

sudo rm -rf /usr/local/go
wget https://go.dev/dl/$GO_TARBALL
tar -C /usr/local -xzf $GO_TARBALL
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
go version
rm -rf $GO_TARBALL