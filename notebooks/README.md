# Instruction on how to run the notebooks
-----------------
* open a jupyter server and run `pip install -r requirements.txt`
* run `pip install intel_extension_for_pytorch==2.0.110+xpu -f https://developer.intel.com/ipex-whl-stable-xpu` (if using xpu enabled device)
* run notebooks using shift+enter to see results, instruction are there on notebook
* preferred order [train and quantize](./train_and_quantize.ipynb) => [submission generation](./submission.ipynb)