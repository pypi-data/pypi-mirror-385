# User requirements installation mechanism (IMPORTANT: possibly out-of-date)

Users can install debian packages and python packages globally in their org.

- Debian packages (referred as system packages in the app) installed with `apt`
- Python packages installed with `pip`

Python packages often depends on system packages.

eg: [librosa](https://pypi.org/project/librosa/) (A python package for music and audio analysis) needs the `ffmpeg` debian package.


## Process

User can specify both of these individually in the frontend. The resulting actions triggers a docker image build.

1. User specify system packages this changes the `PyNodeRequirement` model
2. User specify python packages this changes the `PyNodeRequirement` model
3. A docker build is triggered
  3.1 If this fails we stop here and mark the `PyNodeRequirement` as failed and keep the last working `pynode` image
4. The new `pynode` image is deployed


## Failures

Failures to install a python package might be because of a missing system package.

There is a possiblity that a dependency causes a docker build failure, we currently cannot target which element triggers the failure.

We simply mark the PyNodeRequirement as failed, along with an error_message. This error_message is then shown to the user, on both the System packages and Python requirements pages.

By specifying requirements that don't work, the org may end up with requirements
in a bad state. It is left up to the users of the org to fix the requirements.

## Failures and updates to baseten_internal & common

When we deploy a pynode due to changes on Baseten side, we pick up this
successful version to do the builds. This allows us to rollout Baseten changes.
