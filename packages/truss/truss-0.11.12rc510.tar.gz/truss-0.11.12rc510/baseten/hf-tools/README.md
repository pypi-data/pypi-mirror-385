# HF-Tools

This image contains the `huggingface-cli` and `hf-transfer` CLI tools.

## Usage

This image is used to download models onto Baseten infrastructure. The lightweight image helps us 
avoid running user code while we've mounted R/W node storage.

## Publishing

* You must be authenticated into the baseten docker registry to publish the image.
* Use `./publish.sh` to build and push the image to the baseten docker registry.

## Usage

Once you have an image, you can set the `hf_tools_image` in `operator/core/settings.py` 