#!/bin/bash

if command -v "docker-compose" >/dev/null 2>&1; then
    cmd="sudo docker-compose"
elif command -v "docker" >/dev/null 2>&1 && sudo docker compose version >/dev/null 2>&1; then
    cmd="sudo docker compose"
else
    echo "You don't have Docker Compose installed."
    exit 1
fi

$cmd up -d --build