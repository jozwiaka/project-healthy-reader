#!/bin/bash

set -e

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt -subj "/CN=ingress.internal/O=ingress.internal"
echo "generated ./tls.(crt/key)"