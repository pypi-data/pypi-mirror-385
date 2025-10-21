# Stripe integration

We use Stripe to handle billing, invoicing, and payments related to all customer charges incurred through the Baseten application.

## Developing & testing Stripe integration

### Local setup / Codespaces

- Go to `https://dashboard.stripe.com/` and create a new test account. You can use your Baseten email.
  - This new account only has a _test_ environment. Stripe will prompt you to "Activate payments" in order to enable the _live_ environment but you can ignore/skip this.
- Click the "Developers" link in the top right of the dashboard. Go to the API keys section.
- Set the secret key as the `STRIPE_API_KEY` environment variable when running your Django app.
- Set the publishable key as the `STRIPE_PUBLISHABLE_KEY` environment variable when running the frontend (`npm run start`).
- Create products for the nine paid instance types by running: `python manage.py upsert_stripe_products_for_instances`
  - Note: this command is idempotent so it should be safe to run after the products have already been created. It should also be run after the rare cases of instance type names or display names being updated.
- If you visit https://dashboard.stripe.com/test/products, you should see two products for the Business and Starter tiers and nine for the OracleInstanceTypes.

### Testing webhook forwarding

- Install [Stripe CLI](https://stripe.com/docs/stripe-cli) and login to your Stripe account with `stripe login`
- Run `stripe listen --forward-to http://localhost:8000/integrations/stripe/webhooks` to forward webhooks to your local environment
- Copy the webhook signing secret output by the command
- In a separate shell, set the `STRIPE_ENDPOINT_SECRET` environment variable to the signing secret and run django

### Clusters deployments

The three clusters are each connected to a different Stripe environment, and the API key is provided as a Helm secret:

- Development - Uses matt.howard+stripe-dev@baseten.co in test mode. Password is in 1Password.
- Staging - Uses Baseten Stripe account in test mode. Access is restricted
- Production - Uses Baseten Stripe account in live mode (real money). Access is restricted

## Architectural philosophy

- Use Django models to represent relationships between Baseten objects and their respective Stripe objects when these relationships are important to writing application logic. Don’t rely on the Stripe API to build these associations at runtime.
  - For example, we have the `StripeProduct` and `StripeSubscription` Django models that map directly to objects in Stripe. Even though Stripe is the source of truth for these objects, we have enough information without querying the Stripe API to understand which subscription an organization has and which subscription items that subscription has.
- Keep loose coupling between Baseten core functionality or logic and Stripe-specific or billing-specific code. Billing and subscriptions should be thought of a standalone “service” of the application
  - It’s okay for core Baseten models to reference Stripe-specific data through a field or Stripe-specific objects through a foreign key. Loose coupling doesn’t mean abstracting all Stripe knowledge away.
- The Baseten application, minus billing support, should be able to function completely with an empty `STRIPE_API_KEY` . Even though this key will be set in every cluster environment, it will not be set for most dev environments most of the time.
- The Baseten application should assume the Stripe account it is connected to is multi-tenant, meaning multiple applications or instances of Baseten applications are running alongside one another. While it’s safe to assume the current application has control over the Stripe objects it creates and manages (meaning a single Stripe customer isn’t shared across Baseten applications), it’s not safe to assume there’s exactly one Stripe product named “Business tier”.
  - Both the staging and development clusters use the same Stripe test environment

## Other resources

- [Stripe integration tech spec](https://coda.io/d/_dSCQSpZUKkk/Tech-spec-Stripe-only-billing-infrastructure_su9MY)
