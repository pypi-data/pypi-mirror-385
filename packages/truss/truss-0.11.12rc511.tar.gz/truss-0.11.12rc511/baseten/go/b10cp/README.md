# **b10cp**

b10cp is a Go package for downloading blobs in parallel using the HTTP byte range header.
Currently only tested against AWS S3. It should work with any blob storage service that supports the HTTP byte range
header.

# **cli**

This is a command-line interface (CLI) tool that downloads a blob file from a given URL.

To use this tool, you need to provide the following parameters:

- *-source*: the URL of the blob file to download.
- *-target*: the location where the downloaded file will be saved.
- *-num-workers*: Number of workers to use for the download (default 64)
- *-buffer-size*: Size of the buffer for each worker as a memory string "1MB", "1GB", etc. (default 64MB)

```
go run cmd/cli/main.go -source=https://example.com/myblob -target=/path/to/myfile
```

```azure
go run cmd/server/main.go -addr=:8080
```

The server supports the following configuration parameters:

- *-num-workers*: Number of workers to use for the download (default 64)
- *-buffer-size*: Size of the buffer for each worker as a memory string "1MB", "1GB", etc. (default 64MB)
- *-addr*: Address to listen on (default :3129)

To build the Docker Image and pushing it to the registry, run the following command:

Bump up the version in the Makefile!

```
make deploy-server -e AWS_ACCOUNT_ID=469831140873
```

# proxy server

To run the proxy server, you need to follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the root directory of the cloned repository.
3. Install the required packages using the command: `go get ./...`
4. Generate the SSL/TLS certificates.
5. Run the proxy server using the command: `go run main.go --cert /path/to/cert.pem --key /path/to/key.pem`.

## Generating the Certificates

To generate the SSL/TLS certificates, you can use the following steps:

1. Install OpenSSL on your machine if it's not already installed.
2. Navigate to the directory where you want to store the certificates.
3. Run the following command to generate a private key: `openssl genrsa -out key.pem 2048`
4. Run the following command to generate a certificate signing request (
   CSR): `openssl req -new -key key.pem -out csr.pem`
5. Run the following command to generate a self-signed
   certificate:`openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem`

```
go run main.go --cert /path/to/cert.pem --key /path/to/key.pem --proxy-host localhost --https-proxy-port 3130 --http-proxy-port 3131 --num-workers 64 --buffer-size 64MB --tmp-dir /tmp
```

To test the proxy server, you can use the following command:

```
curl -x https://localhost:3130 -k https://google.com -v
curl -x http://localhost:3131 -k http://google.com -v
```

## How to test locally in the operator

For instructions on testing changes locally, see the "How to test locally" in [dockerfiles.md](../../docs/how-to/dockerfiles.md). The image tag should be updated in both `operator/core/settings/local.py` and `operator/core/settings/minikube.py`.

## How to roll out a new image

New images should be picked up automatically in staging and dev by FluxCD. To release a new version to prod, promote the `image/baseten/b10cp` artifact using CDLI.
