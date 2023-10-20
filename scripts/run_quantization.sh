#!/bin/bash

# Prompt the user for a single argument
echo "Enter Pruned Model path:"
read arg

# Check if an argument was provided
if [ -z "$arg" ]; then
    echo "No argument provided. Exiting."
    exit 1
fi

python3 quantize.py \
    --model_name_or_path "$arg" 
