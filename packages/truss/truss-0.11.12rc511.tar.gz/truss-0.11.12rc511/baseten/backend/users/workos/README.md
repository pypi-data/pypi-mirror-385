# WorkOS

WorkOS is our new authentication provider, handling Magic Auth + SSO login flows for us.

## Configuration

Our deployed clusters map 1:1 with our WorkOS environment names. There are a few scoped keys/secrets that are required for the
integration to work:
- WORKOS_API_KEY
- WORKOS_CLIENT_ID

These are configured in AWS secrets manager, and plumbed as k8s secrets via Terraform. Then, they're setup as environment variables
in the Django chart.

We also need a `WORKOS_HOSTED_LOGIN_URL` which is our new login / signup page completely hosted by WorkOS. This value is managed
via flux per cluster.

## DNS Configuration

We need to manually maintain DNS aliases to WorkOS so the integration is transparent, specifically in the production environment:
- `login.baseten.co` -> `cname.workos-dns.com` (hosted Login page)
- `auth.baseten.co` -> `cname.workos-dns.com` (SSO / most OAuth callbacks)
- `auth-social.baseten.co` -> `cname.workosdns.com` (Google OAuth callback - intentionally without the dash)
- `auth-setup.baseten.co` -> `cname.workos-dns.com` (SSO onboarding Admin portal)

WorkOS does not allow custom domains for non-production environments, so these are only provisioned once.

All of these CNAMEs are manually registered via AWS Route53
