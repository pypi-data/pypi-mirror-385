# Dev Setup

## Git & Github settings

Set up slack pull request reminder. https://github.com/settings/reminders/basetenlabs

### Set Up Git SSH

1. Check for existing SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys

2. Generate a SSH Key and add to ssh-agent: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

3. Add SSH key to GitHub: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account

# Set up Dev Environment

There are two options for development at Baseten:

- [Local Development](Local-Development.md)
- [Github Codespaces](Github-Codespaces.md)

We recommend using Codespaces, where the development environment is consistent and up-to-date.

_If you plan to work on model serving then Codespaces is the only way we support right now, Truss dev environment wouldn't even work on m1 macs._

# Setting up your User in Development

At Baseten, several features are gated -- behind feature flags as well as license/plan selection.
As you develop, you might want to grant access to these features. You can do this through using
the [Billip](http://localhost:8000/billip) on your local instance.

**Please pair with another engineer if making changes on production billip.**

## Enabling Feature Flags

You can enable a specific feature flag for your user by visiting the flags page, clicking a flag,
and enabling it for your development org.

**Visiting Flags Page:**
![Flag Selection Page](images/flags-page.png)

**Enabling for your development user**

![Flag Update Page](images/specific-flag-page.png)

Click all of the permissions for your development user, and then click "Save"

## Enabling Higher License Tier

In order to enable paid features -- the way to do this is to enable "License Customizability"
on your development user.

![License Customizability](images/license-custom-toggleability.png)

You can then go into the License for your user and make the changes that you need to make.

# Additional Tools

- [editorconfig](http://editorconfig.org/)
- Frontend tools
  - [ESLint](http://eslint.org/)
  - [React devtools Chrome extension](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
  - [Recoil Toolkit Devtools Chrome extension](https://chrome.google.com/webstore/detail/recoiljs-devtools/kegjgkcfjocgpdhjgjgjgkghjgjgjgda?hl=en)
  - [ChromeiQL](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi) - Allows running GraphQL queries against prod or staging. Just sent the endpoint to https://app.baseten.co/graphql/ or https://app.staging.baseten.co/graphql/

# Troubleshooting

### Database Errors

Sometimes, old udm databases get stuck, which will cause the `create_dev_db.sh` script to fail. They can be cleaned up manually. Rerunning the script should work after that.

```
psql

# in psql, list all databases
\l

# Delete databases starting with "b10_udm_", if any
DROP DATABASE db_name;

# use \q to quit psql when you are done
```

### Minikube Errors

Sometimes, the `local_cluster_setup.sh` script will fail silently, leaving the minikube cluster in an incomplete state. Most often, it is one of the components installed by `helmfile` that had an issue. You can do the following to validate and fix.

```
# Check you helm installation. It should print this
# NAME   	VERSION   	DESCRIPTION
# diff   	3.1.3     	Preview helm upgrade changes as a diff
# secrets	3.12.0-dev	This plugin provides secrets values encryption [...]
helm plugin list

# If your helm installation is not correct, go back to the "Prerequisite tools" section of
# this document and install the required tools

# Check your kubernetes setup. A brand new installation should look like this
# NAMESPACE          NAME                                                              READY   STATUS
# cert-manager       cert-manager-7c6f78c46d-lx6ch                                     1/1     Running
# cert-manager       cert-manager-cainjector-668d9c86df-g728k                          1/1     Running
# cert-manager       cert-manager-webhook-764b556954-wq7h8                             1/1     Running
# istio-system       istio-ingressgateway-798855948b-nwzq4                             1/1     Running
# istio-system       istiod-58d79b7bff-z7dnh                                           1/1     Running
# knative-serving    activator-c8db4fbd8-mp568                                         1/1     Running
# knative-serving    autoscaler-b84d7964d-sgfxh                                        1/1     Running
# knative-serving    controller-8594bdbb59-hq2gv                                       1/1     Running
# knative-serving    domain-mapping-7f769f9cb7-ghvmb                                   1/1     Running
# knative-serving    domainmapping-webhook-5b4f95d4d7-6s5x6                            1/1     Running
# knative-serving    net-istio-controller-86b67bc8-dwcrr                               1/1     Running
# knative-serving    net-istio-webhook-65fb676674-5bh7g                                1/1     Running
# knative-serving    webhook-695bd9d564-6zjfb                                          1/1     Running
# kserve             kserve-controller-manager-0                                       2/2     Running
# kube-system        coredns-558bd4d5db-pcggk                                          1/1     Running
# kube-system        etcd-baseten-local                                                1/1     Running
# kube-system        kube-apiserver-baseten-local                                      1/1     Running
# kube-system        kube-controller-manager-baseten-local                             1/1     Running
# kube-system        kube-proxy-g5h6g                                                  1/1     Running
# kube-system        kube-scheduler-baseten-local                                      1/1     Running
# kube-system        registry-proxy-r66pd                                              1/1     Running
# kube-system        registry-rm85c                                                    1/1     Running
# kube-system        storage-provisioner                                               1/1     Running
# logging-user       loki-user-0                                                       1/1     Running
# logging-user       promtail-user-qlhw4                                               1/1     Running
# logging            loki-0                                                            1/1     Running
# logging            promtail-vhfkk                                                    1/1     Running
# tekton-pipelines   tekton-pipelines-controller-78d8d6d4b-tv24h                       1/1     Running
# tekton-pipelines   tekton-pipelines-webhook-64fd67d65-czpw9                          1/1     Running
kubectl get pods -A

# If you are missing anything in "tekton-pipelines" or "knative-serving" namespace, you can fix be rerunning the helmfile
cd helm/helmfile
helmfile -e local sync
```

### Pynode Build Errors

Building a pynode requires access to S3.
On M1, you also need to have set the [MINIKUBE_SERVING_HOST and MINIKUBE_SERVING_INGRESS_PORT environment variables](#m1-setup). You can validate both the aws-vault context and the MINIKUBE_SERVING variables like this:

```sh
echo $MINIKUBE_SERVING_HOST
echo $MINIKUBE_SERVING_INGRESS_PORT
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# If any of those are empty, building the pynode will fail.
# Refer to the correct section of this documentation for details
```

### Server is not reacheable

Everything is running correctly, but when you try to load `localhost:8000`, it doesn't do anything and there is no error in the django server logs? You might have some other software using the 8000 port. You can use `sudo lsof -i -P | grep LISTEN | grep :$PORT` to see which ports are currently used on your local computer.

```
#> sudo lsof -i -P | grep LISTEN | grep :$PORT
Spotify     597 jonathanrochette  106u  IPv4 0x4ac18930020b0691      0t0    TCP *:49178 (LISTEN)
Spotify     597 jonathanrochette  107u  IPv4 0x4ac18930020afbf9      0t0    TCP *:57621 (LISTEN)
ControlCe   607 jonathanrochette   19u  IPv4 0x4ac1893001733bf9      0t0    TCP *:7000 (LISTEN)
ControlCe   607 jonathanrochette   20u  IPv6 0x4ac1892b32c169b1      0t0    TCP *:7000 (LISTEN)
ControlCe   607 jonathanrochette   21u  IPv4 0x4ac1893001733161      0t0    TCP *:5000 (LISTEN)
ControlCe   607 jonathanrochette   22u  IPv6 0x4ac1892b32c170b1      0t0    TCP *:5000 (LISTEN)
WeirdStuff  444 jonathanrochette   22u  IPv6 0x4ac1892b32c170b1      0t0    TCP *:8000 (LISTEN)
redis-ser   841 jonathanrochette    6u  IPv4 0x4ac18930022a9bc1      0t0    TCP localhost:6379 (LISTEN)
redis-ser   841 jonathanrochette    7u  IPv6 0x4ac1892b32c18cb1      0t0    TCP localhost:6379 (LISTEN)
postgres    847 jonathanrochette    7u  IPv6 0x4ac1892b32c193b1      0t0    TCP localhost:5432 (LISTEN)

# The WeirdStuff process is using 8000. Let's kill it
#> kill -9 444
```

### Ctags

If you plan to use the command line for development, you may want to install and build ctags for the python code in this repository. Universal ctags can be installed [here](https://github.com/universal-ctags/ctags) and the `make ctags` command from the root of this repo can be used to build a `baseten/.ctags` file for use. You should then refer to this ctags file from your text editor of choice.
