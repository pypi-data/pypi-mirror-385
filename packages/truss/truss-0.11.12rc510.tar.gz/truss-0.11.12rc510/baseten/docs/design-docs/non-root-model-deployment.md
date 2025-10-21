# Non root model deployment
For security reasons, we need to run the model container (and the side cars) without escalated privileges.

## Current state
The model container and the proxy side car are all running as root user.
There were couple of reasons behind this
- Truss base image uses system space to install packages, which requires root privilege.
- b10cp
  b10cp is a MITM (man in the middle) proxy, which intercepts the requests to the target host. When the target host uses HTTPS protocol, the client uses the server certificate to verify/trust the remote host. This requires the MITM proxy to issue a certificate using the target hostname as the CN to present to the client, and the client also needs to trust the certificate from the MITM proxy, e.g. the client has the CA that is used to issue the b10cp certificate (intermediate CA)
  
  With the approach, the proxy container (b10cp) needs to generate a self signed CA and use it to issue the target host certificates
- model container needs to check and retrieve the b10cp CA certificate, and add it to the trusted CA bundle. This requires **root** privilege

## The new approach
In order to address the problems above, we need to have a method to
- Generate the CA certificate ahead of time
- Generate the intermediate CA for b10cp when the customer's namespace is created
- Make the root CA available for the model container when it is being created
- Use b10cp intermediate CA to issue the MITM certificate when the client (model container) makes a https request

[Cert-Manager](https://cert-manager.io/) can help us to issue certificates, and it's addon, [trust-manager](https://cert-manager.io/docs/trust/trust-manager/), can help us to manage the CA certificates bundles.

- To begin with, a root CA certificate is created (cluster level), and a cluster issuer (can issue certificate to any namespace) is created to use that CA certificate.
- The cluster level CA certificate is then put into a bundle with the other publicly trusted CA certificates, for example, apple.com, google.com, etc. This bundle will be ingested into namespaces that match the selector `baseten.co/organization: "true"` as a configMap (secret is not supported on lower versions)
- When the model container is deployed, it will mount the configMap to `/etc/ssl/certs` and all the certs in the bundle is then trusted
- When the model container makes a https request, say https://foo.bar, through b10cp, b10cp will use it's certificate (intermediate root) to issue a cert with CN `foo.bar` and presents it back to the model container. Since b10cp's certificate is issued by the CA in the bundle, the certificate is trusted.
  
[This](https://docs.mitmproxy.org/stable/concepts-howmitmproxyworks/) doc explains MITM proxy very well if you wish to get more details. 
