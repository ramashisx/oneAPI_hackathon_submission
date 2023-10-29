#!/bin/bash

# Enable the "set -e" option to exit on error
set -e

# Prompt the user for a single argument
echo "Enter Trained Model path:"
read arg

# Check if an argument was provided
if [ -z "$arg" ]; then
    echo "No argument provided. Exiting."
    exit 1
fi

python3 prune.py \
    --model_name_or_path "$arg" \
    --num_warmup_steps 500 \
    --num_train_epochs 3 \
    --cooldown_epochs 1 \
    --train_file ../data/train_processed.csv \
    --validation_file ../data/valid_processed.csv \
    --output_dir "../sparse-T5-QA" \
    --per_device_train_batch_size 16 \
    --per_device_eval_batch_size 16 \
    --checkpointing_steps 'epoch' \
    --weight_decay 5e-04 \
    --target_sparsity 0.8 \
    --pruning_pattern "4x1" \
    --pruning_frequency 50000 \
    --learning_rate 1e-03
