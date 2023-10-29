#!/bin/bash

# Enable the "set -e" option to exit on error
set -e
set -o pipefail

MODEL_DIR="./model"
MODEL_ZIP="./model.zip"
GOOGLE_DRIVE_LINK="https://drive.google.com/uc?id=10ILW2lC1ecktK_q16bTD83qJPDqTNCds&export=download"
EXPECTED_DIR_CHECKSUM="02ced3792e90a829ca45e2141b68934b"
EXPECTED_ZIP_CHECKSUM="d86de200085040b565abdd873148665a"

# Function to check the checksum of a directory
check_directory_checksum() {
    if [ -d "$1" ]; then
        checksum=$(checksumdir "$1" -e md5)
        if [ "$checksum" == "$EXPECTED_DIR_CHECKSUM" ]; then
            echo "Checksum is correct for $1"
            return 0
        else
            echo "Checksum is incorrect for $1"
            echo "If you are getting this error in loop make sure checksumdir is installed, make sure you did install requirnments from this folder"
            return 1
        fi
    else
        echo "$1 does not exist."
        return 1
    fi
}

# Check if the model directory exists
if [ -d "$MODEL_DIR" ]; then
    # Check if the model directory has the correct checksum
    if check_directory_checksum "$MODEL_DIR"; then
        echo "Model directory is valid. No further action is required."
    else
        echo "Model directory is invalid. Removing it."
        rm -rf "$MODEL_DIR"
    fi
fi

# If the model directory does not exist, proceed to check the model.zip file
if [ ! -d "$MODEL_DIR" ]; then
    if [ -f "$MODEL_ZIP" ]; then
        # Check the MD5 checksum of the file
        file_checksum=$(md5sum "$MODEL_ZIP" | awk '{print $1}')
        echo $file_checksum
        if [ "$file_checksum" == "$EXPECTED_ZIP_CHECKSUM" ]; then
            echo "Model.zip checksum is correct. Extracting the model..."
            # Unzip the model
            unzip "$MODEL_ZIP" -d "$MODEL_DIR"
            if check_directory_checksum "$MODEL_DIR"; then
                echo "Model is valid."
            else
                echo "Model is invalid. Please check the integrity of the extracted files."
            fi
        else
            echo "Model.zip checksum is incorrect. Downloading a new model..."
            # Download the model from Google Drive
            gdown "$GOOGLE_DRIVE_LINK" -O "$MODEL_ZIP"
            
            # Unzip the model
            unzip "$MODEL_ZIP" -d "$MODEL_DIR"

            # Check the checksum of the unzipped model
            if check_directory_checksum "$MODEL_DIR"; then
                echo "New model is valid."
            else
                echo "New model is invalid. Please check the download source."
            fi
        fi
    else
        echo "Model.zip does not exist. Downloading a new model..."
        # Download the model from Google Drive
        gdown "$GOOGLE_DRIVE_LINK" -O "$MODEL_ZIP"
        
        # Unzip the model
        unzip "$MODEL_ZIP" -d "$MODEL_DIR"

        # Check the checksum of the unzipped model
        if check_directory_checksum "$MODEL_DIR"; then
            echo "New model is valid."
        else
            echo "New model is invalid. Please check the download source."
        fi
    fi
fi


# Start the Uvicorn server in the background
uvicorn api.main:app --reload --port 4444 &

# Wait for 5 seconds for server to boot up
sleep 5

# Start the Streamlit app in the background
streamlit run ./ui/main.py --server.port 4445 &

# Wait for both servers to pu logs
wait
