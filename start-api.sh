#!/bin/bash

if command -v "docker-compose" >/dev/null 2>&1; then
    cmd="docker-compose"
elif command -v "docker" >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    cmd="docker compose"
else
    echo "You don't have Docker Compose installed."
    exit 1
fi

$cmd up -d --build