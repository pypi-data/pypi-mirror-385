# Add or Update a Model Library Model

Baseten has a model library of pretrained models available at https://app.baseten.co/explore,
where users can click through to deploy these existing models into their account.

The canonical source of all of these models, including the display information, is Github. The process
for adding a new model or updating a model in the library is as follows:

1. Get the Truss for the model into a good state in Github
2. Submit the [Add or update model library model form](https://app.baseten.co/billip/oracles/addmodellibrarymodelpage/)
3. Update the model library whitelist
4. [For existing models] Promote latest version to primary
  
# Modifying the Truss

Each of the models in the model library is backed by a Truss on Github. In order to get one of these trusses into the
library, the config for the Truss must include the following fields filled out:

* model_name
* description
* model_metadata.avatar_url
* model_metadata.cover_image_url
* model_metadata.tags

This data will be used to serve the model cards on the explore page.

So, the YAML must look like this:

```
...
description: StableLM is an open-source AI language model developed by StabilityAI
model_metadata:
  avatar_url: https://cdn.baseten.co/production/static/explore/stability.png
  cover_image_url: https://cdn.baseten.co/production/static/explore/stable-lm.png
model_name: StableLM
...
```

See https://github.com/basetenlabs/stablelm-truss for an example.

# Submitting the form

Visit: https://app.baseten.co/billip/oracles/addmodellibrarymodelpage/, and fill out the following:

* Model Name -- this is a short slug, like "stable_diffusion" or "whisper".
  * If you are updating an existing model, this *must* match what you are updating. If you are not sure,
  check the `LIBRARY_MODELS_WHITELIST_JSON` in the Constance config for the correct value
* Github URL -- link to the Github Repo with the Truss https://github.com/basetenlabs/stablelm-truss.git
* SHA -- the correct SHA from the repo to use

It'll take a few seconds to submit. Keep in mind that what governs whether models show up on the /explore page
is whether they are present in the `LIBRARY_MODELS_WHITELIST_JSON` constant or not. Submitting this form **does not** automatically
add it, you'll have to do it separately.

# Updating the Library Models Whitelist

Submitting the form will kick off a build for your model. Once the build is complete, for the
model to show up on the /explore page, add it to the `LIBRARY_MODELS_WHITELIST_JSON` on the [Constance Dashboard](https://app.baseten.co/billip/constance/config/). This constant governs what shows up on the /explore page.

# [Updates Only] Promote the Latest Version to Primary

If you are updating an existing model, the new version won't take effect until you **Promote it to Primary**. After saving model in Billip, a deployment will be spun up in Baseten’s admin account. To access the admin account, you can hijack it via billip. The email is admin@baseten.co. Once hijacked, monitor the model to make sure it deploys without any failures.

# Removing a model

If something is wrong with your model, and you'd like to remove it from the Explore page, modify the
`LIBRARY_MODELS_WHITELIST_JSON`  constant on https://app.baseten.co/billip/constance/config/.
