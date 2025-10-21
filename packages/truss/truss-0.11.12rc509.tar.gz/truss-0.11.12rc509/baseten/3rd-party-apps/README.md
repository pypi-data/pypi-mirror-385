# Purpose

We need a way to build images off 3rd party repos but not necessarily forking their repos.
Use this folder to host the configuration of the jobs and build/push from the GH action workflows.

## How
- Clone the 3rd party repo
- Duplicate the files need to be modified
- Modify the files
- Run `diff -u` to generate patch file and place it under the `3rd-party-apps/<app-name>` folder (combine all patches into one file)
- Create a `config.yaml` file in the folder
- Create a patch file, make sure the patch level should be `-p0` 
