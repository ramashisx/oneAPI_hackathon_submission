# This is the web app codes
-----------------------------


### How to get started
* Make sure you are running it on intel infrastructure
* run `pip install -r requirnments.txt`
* run `bash run.sh`
* If you are running on a remote instance make sure you port forward two ports by running
* run `ssh myidc -L 4444:10.10.10.X:4444` and `ssh myidc -L 4445:10.10.10.X:4445`
* replace `10.10.10.X` with the Public IP of your remote machine
* after running connect to `localhost:4444` for backend `localhost:4444/docs` for api documentation
* connect to `localhost:4445` for UI
* This script will take care of everything the backend server integrity of model files and downloading new model files.
* To use this webapp for different model make sure you change the md5checksum values in this bash [script](./run.sh)


![](../assets/webapp.png)
