#!/bin/bash

# Prompt the user for a single argument
echo "Enter the Model path from which you want to generate submssion:"
read arg

# Check if an argument was provided
if [ -z "$arg" ]; then
    echo "No argument provided. Exiting."
    exit 1
fi

python3 submission.py \
    --model_name_or_path "$arg"
