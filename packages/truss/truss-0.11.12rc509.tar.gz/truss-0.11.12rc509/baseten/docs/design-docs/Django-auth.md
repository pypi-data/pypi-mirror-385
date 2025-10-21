# Django application auth

This document outlines how we handle authentication and authorization for requests to our Django application. Although Django has built-in support for authorization and permissioning, by layering in our own middleware and view decorators, we can better adhere to the principles of [Security by Design](https://en.wikipedia.org/wiki/Secure_by_design), including:

- Principle of Least Privilege - provide only the required access based on user role and credential type
- Strong Authentication and Authorization - centralized, well tested authentication logic
- Secure Defaults - assumes restrictive access controls per endpoint, and loosening controls requires explicit override
- Simple Design - Usage of the system is simple and encourages code reuse and strong patterns, thereby reducing room for error or oversight

## System architecture

Our auth system relies on several components:

- **`@auth` decorators** for every view and every root GraphQL query and mutation.
  - _We'll focus on views below for brevity but the same rules apply to the GraphQL endpoints_
  - These auth decorators assign each view a `auth_options: ViewAuthOptions` attribute describing the permissions required by that view
  - If a view lacks a decorator, any requests to it will return a 500 as a fail-safe.
  - See [auth_decorators.py](backend/users/authorization/auth_decorators.py)
- **Permission check** functions
  - Permission checks are functions that are given information about the request in the form of a `PermissionCheckContext` object
  - They can:
    - Raise a `PermissionDenied` exception
    - Return a `HttpResponse` directly, preventing further handling of the request (see `requires_approval()` for an example).
      - Note that the function should only return an HTTP redirect if `allows_redirect=True` is set on the `PermissionCheckContext`.
    - Return `None` to allow a request to proceed
    - Inspect request kwargs ([captured parameters](https://docs.djangoproject.com/en/4.2/topics/http/urls/#captured-parameters) for views and query/mutation parameters for GQL endpoints) and replace them with **authenticated objects**.
      - For example, the `manage_model` check pops the `model_id` kwarg and sets an `oracle: Oracle` object that gets passed to the resulting view. From the view's standpoint, the oracle object is proof that the request has permission to operate on the object and there's no need to call `get_object_or_404` inside the view. By popping (removing) the `model_id` keyword, we reenforce this object passing pattern and reduce the chance of incorrect object lookups.
  - The `ViewAuthOptions` specified by the `@auth` decorators contains default permission checks (see `DEFAULT_PERMISSION_CHECKS`) and at least one explicit permission check.
    - If you're unsure which permission check to specify, please ask for help. Specifying the wrong permission check can lead to security vulnerabilities or broken functionality.
  - See [permission_checks.py](backend/users/authorization/permission_checks.py)
- `BasetenAuthMiddleware`
  - The middleware **authenticates** the user (resolves a user object for the particular request) in the main middleware stack.
    - The authentication process does not depend on the resolved view and its `ViewAuthOptions`.
    - The resolved user is set on `request.context` and on the `django_context_crum` context. It also sets `request.auth_type: AuthType` so downstream logic can tell how the request was authenticated.
    - Each means of authentication is implemented by an [AuthenticationProvider](backend/users/authorization/auth_provider.py), except for Django session auth which is handled by `django.contrib.auth.middleware.AuthenticationMiddleware`.
  - The middleware **authorizes** the request for the view in `process_view`, using the view's `ViewAuthOptions` object. It runs each permission check and only allows the request to proceed if all checks pass. It also passes any authorized objects to the view.
  - See [middleware.py](backend/users/authorization/middleware.py)
- `GrapheneAuthMiddleware`
  - This checks performs authorization on each root GraphQL query and mutation, just like the `BasetenAuthMiddleware` does for Django views. Authentication is still provided by the `BasetenAuthMiddleware`.
  - See [graphql_middleware.py](backend/users/authorization/graphql_middleware.py)

## Org-level auth decorators

Some permissions checks are org-level (e.g. see `manage_org_models`), meaning they don't authenticate against a specific object instance. Instead, they check that the user has the given permission at the organization level, which normally applies to all workspace objects. These are useful for views that don't take in a specific model object (e.g. views that create a model). It's still better to use a bound permission check if possible, since the authenticated objects are less prone to error and permit more granular permissions.
