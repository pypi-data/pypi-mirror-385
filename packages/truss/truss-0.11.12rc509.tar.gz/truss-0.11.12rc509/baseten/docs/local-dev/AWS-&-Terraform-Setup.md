# Tools installation

It is highly recommended to use aws-vault. aws-vault stores credentials in the OSX keychain, more info here:
https://github.com/99designs/aws-vault

```sh
# Local mac instructions
# Install aws-vault & terraform
# https://github.com/99designs/aws-vault
brew install --cask aws-vault
brew install terraform awscli

# Install on a codespace
asdf plugin-add aws-vault https://github.com/karancode/asdf-aws-vault.git
asdf install aws-vault <version>
asdf global aws-vault <version>
```

## Log into aws

```sh
aws configure
```

## Set up your aws profile

```sh
aws-vault add <profile-name> ## this can be anything but remember it

# If installing on a codespace, you'll need to use a encrypted file instead of the keychain
aws-vault add <profile-name> --backend=file
```

## Set up "role switch" in cli

In `$HOME/.aws/config`, add the following, replacing `<vault profile name>` with the profile name you used in the previous step and `<your aws mfa serial>` with your mfa serial. It should look something like `arn:aws:iam::836885557665:mfa/user.name`.

```ini
[default]
region=us-west-2

[profile <vault profile name>] # (should have been created automatically by aws-vault)

[profile production]
source_profile = <vault profile name>
role_arn = arn:aws:iam::836885557665:role/administrator
mfa_serial = <your aws mfa serial>

[profile cp-prod-1]
source_profile = <vault profile name>
role_arn = arn:aws:iam::836885557665:role/administrator
mfa_serial = <your aws mfa serial>

[profile us-west-2-prod-1]
source_profile = <vault profile name>
role_arn = arn:aws:iam::836885557665:role/administrator
mfa_serial = <your aws mfa serial>

[profile staging-cluster]
source_profile = <vault profile name>
role_arn=arn:aws:iam::094050715936:role/administrator
mfa_serial = <your aws mfa serial>

[profile dev-cluster]
source_profile = <vault profile name>
role_arn=arn:aws:iam::469831140873:role/administrator
# dev cluster doesn't require MFA
```

As additional EKS clusters are spun up, you can add more profiles to this file. If the cluster is located outside of `us-west-2`, you can override the `region` in the cluster's sub-profile.

## Connect to the cluster

```sh
aws-vault exec staging-admin -- <cmd>
# Codespace version
aws-vault exec staging-admin -- <cmd> --keychain
# Eg:
aws-vault exec staging-admin -- terraform plan
aws-vault exec staging-admin -- aws s3 ls

## Export env vars to a subshell
aws-vault exec staging-admin
```

Once you have the creds set up like above, you can add prod cluster to kube config like this:

```sh
# LOAD PROD CREDS
aws eks --region us-west-2 update-kubeconfig --name production
```

```sh
# LOAD STAGING CREDS
aws eks --region us-west-2 update-kubeconfig --name staging-cluster
```

### Using aliases

You can also use the [avs](../../bin/baseten_aliases.sh) alias from inside an `aws-vault` subshell to set the kube config context:

```sh
aws-vault exec staging-admin
avs
```

If your session token expires, you can refresh it with:

```sh
avr
```

## Troubleshooting

If after running this command, you see the error:

```
aws-vault: error: exec: Error getting temporary credentials: profile sid: credentials missing
```

it's possible that you need to re-run the `aws-vault` command. Run `aws-vault ls` to see if
credentials have been loaded for your profile, it should look like this:

```
Profile                  Credentials              Sessions
=======                  ===========              ========
default                  -                        -
sid                      sid                      -
prod-admin               -                        -
staging-admin            -                        -
dev-admin                -                        -
```

# Set up "role switch" in console.aws.amazon.com

Click one of the following links:

- **production**:
  https://signin.aws.amazon.com/switchrole?roleName=administrator&account=baseten&displayName=production-admin
- **staging**:
  https://signin.aws.amazon.com/switchrole?roleName=administrator&account=baseten-staging&displayName=staging-admin
- **dev**:
  https://signin.aws.amazon.com/switchrole?roleName=administrator&account=baseten-dev&displayName=dev-admin

or

1. On top right menu click your username
2. Click "switch role"

![image](https://user-images.githubusercontent.com/2339610/156179133-bc029063-0ce6-4997-90e5-9121c10de49b.png)

3. Fill the role information you want to assume, eg:

```
Account: 094050715936
Role: administrator
Display Name: staging-admin
```

![image](https://user-images.githubusercontent.com/2339610/156179231-1aeced47-afc2-4b2b-a1cf-eb22b153007c.png)

# Looms

[Tips on using shell_plus on dev cluster](https://www.loom.com/share/7bcabb24392443b0b4d16386e99bc0a6)

# Freeing a terraform lock

It is possible that a lock was taken but never released e.g. failures with github workflow jobs.
When this happens, terraform will fail acquiring the lock. Example of error message:

```
╷
│ Error: Error acquiring the state lock
│
│ Error message: ConditionalCheckFailedException: The conditional request failed
│ Lock Info:
│   ID:        1b8cdd15-6955-a013-500f-41694242367a
│   Path:      baseten-terraform-development-states/environments/development.tfstate
│   Operation: OperationTypeApply
│   Who:       runner@fv-az712-500
│   Version:   1.5.7
│   Created:   2023-09-28 21:09:33.651883002 +0000 UTC
│   Info:
```

To free the lock:

1. Open a aws-vault shell with the corresponding env admin role
2. Go to the `basten` repo
3. Go to `terraform/environments/<env>`
4. Run `terraform init`
5. Run `terraform plan` , this should result in the error message with the lock information
6. Run `terraform force-unlock -force <lock id>`
