#!/bin/bash

PUID=${PUID:-9000}
GID=${PGID:-9000}

usermod -u "$PUID" listener
groupmod -g "$GID" listener

chown -R listener:listener /etc/coredns && chown -R listener:listener /tmp/repos

gosu listener gunicorn main:app -w 2 --threads 2 -b 0.0.0.0:5000