#!/bin/bash

# Enable the "set -e" option to exit on error
set -e
set -o pipefail

# Start the Uvicorn server in the background
uvicorn api.main:app --reload --port 4444 &

# Wait for 5 seconds for server to boot up
sleep 5

# Start the Streamlit app in the background
streamlit run ./ui/main.py --server.port 4445 &

# Wait for both servers to pu logs
wait
