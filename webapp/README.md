# This is the web app codes
-----------------------------


### How to get started
* Make sure you are running it on intel infrastructure
* run `pip install -r requirements.txt`
* run `pip install intel_extension_for_pytorch==2.0.110+xpu -f https://developer.intel.com/ipex-whl-stable-xpu` (if using xpu enabled device)
* run `bash run.sh`
* If you are running on a remote instance make sure you port forward two ports by running
* run `ssh myidc -L 4444:10.10.10.X:4444` and `ssh myidc -L 4445:10.10.10.X:4445`
* replace `10.10.10.X` with the Public IP of your remote machine
* after running connect to `localhost:4444` for backend `localhost:4444/docs` for api documentation
* connect to `localhost:4445` for UI
* This script will download the model from huggingface to use a different model change the model name in model [file](./api/main.py)


![](../assets/webapp.png)
