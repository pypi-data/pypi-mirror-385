# Feature Flags

We use [django-waffle](https://github.com/django-waffle/django-waffle) for creating feature flags. [Here](https://basetenlabs.slack.com/archives/C014JUXFGLU/p1667240260665729)'s a bit of context on how we've implemented role-based access control (RBAC) and how waffle fits in.

## Feature flag best practices

We use feature flags provided by Django Waffle extensively throughout both the frontend and backend codebase. The following is an opinionated view of feature flags based on industry best practices.

- **Feature flags are for decoupling continuous deployment from the controlled roll-out of a feature or code change.** They are _not_ meant for configuration (changing the applicate state for a particular environment or set of users).
  - We have other, better ways of managing configuration, like constance, helm values, license fields, and org-level settings
- “It is a good practice to keep feature flags are short-lived as possible. Keeping their number low is equally important.” - Quoted from [this Medium article](https://thysniu.medium.com/coding-with-feature-flags-how-to-guide-and-best-practices-3f9637f51265)
  - A feature flag should only live as long as the change is being actively developed and rolled out. Once a feature is stable, the flag should be removed as soon as possible.
  - Each feature flag introduces more application states. Because we don’t have a great way to keep flag values synced across environments (local dev, staging, prod, self-hosted), it’s easy to get into a state where certain behaviors, and therefore bugs, happen in some environments and not others. **Overall, more flags make it harder to test, develop on, and support the application**.
  - One specific example of this issue is that a fresh dev environment like a codespace doesn’t have any flags enabled, and this is a common source of confusion for developers as their environment doesn’t match what’s in prod, staging, or dev
- Think of structuring flags as deploying two versions of the code, an old one and a new one, at the same time
  - Prioritize the readability and maintainability of the new feature-flag-enabled path while preserving the behavior exactly of the old path.
  - ✅ Good: `if (flag_is_enabled) { // new logic } else { // old logic }`
  - Write the forked logic to make flag cleanup as quick and simple as possible. This both minimizes the risk of regressing logic in the cleanup process and lowers the mental barrier to completing the cleanup work.

## Playbook

These playbooks are meant to be a template for how we think about flags. There will be situations that don’t fit these playbooks exactly, and it’s important to think through and call out the deviations when they occur.

### Standard playbook

1. Create a feature flag following the process below ("How to create a new feature flag"). The flag should pertain to a new feature, behavior, or implementation.
2. Add the new functionality gated behind the new flag. Enable and disable the flag locally to test the old and new behaviors. Write or adapt unit tests that run with the flag on.
3. Enable the flag for everyone on staging and test it, like with a bug bash. Fix any issues and address feedback. You can leave the feature on in staging during this time if the feature is in a usable state or turn it off if there are serious issues.
4. Once all the blocking bugs have been addressed, enable the flag for everyone on production.
5. After the next deploy to self-hosted environments (stability), enable the feature flag there as well
6. Give the feature some [soak time](https://en.wikipedia.org/wiki/Soak_testing). This is the period during which if a critical bug occurs, you’ll turn the feature back off and get into the previous, known good state.
7. After the feature has been on and working for a sufficient time (this is very dependent on the situation), clean up the flag from the source code. See "Deleting a Feature Flag" below.

### Rolling back a flag

Sometimes there are unexpected issues after enabling a feature flag that weren’t caught during earlier testing. In this case, you can temporarily disable the feature flag while you make a forward fix to the new behavior, or in some cases you may want to scrap the feature altogether. In the latter case, called a “no ship” decision, you should remove the feature flag as well as return all the affected code to its original state (the fork of the code that ran when the flag was disabled).

### Piloting new features with certain orgs

You can split up enabling the feature on each environment into two steps:

First, enable the feature for pilot (early adopter) organizations. This is a good way to get early feedback from customers or to test the feature with internal users first. Find the organization id(s) and on the flag’s waffle page in Billip, enable the flag for all groups with that ID. It should look something like this

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9596ee7c-dabd-49c1-a26d-426219d2c59d/Untitled.png)

Then once you’re ready, enable the feature for everyone.

Note that the pilot should not be long lived and the feature flag should be enabled for everyone or disabled for everyone eventually.

## How to create a new feature flag

Adding a new feature flag to Baseten is a fairly easy, albeit nuanced, two-step process.

### The Easy Part: Define the Flag

All backend feature flags are stored in [`backend/feature_flags/flags.py`](/backend/feature_flags/flags.py), so you'll want to define a constant there to track it.

If you plan on using the flag on the frontend, you'll also want to add the same constant (with the same value) to [`frontend/hooks/useFeatureFlags/types.ts`](/frontend/hooks/useFeatureFlags/types.ts).

### The (Not-So-Easy) Part: Create a Manual Migration

We need to create our own migrations to add our flags to the database. A good example of this is the [migration for the pricing paywall flag](/backend/users/migrations/0072_auto_20220817_1744.py).

Adding a new migration is as simple as creating a blank migration on the command-line via:

```
$ uv run python manage.py makemigrations [app name] --empty
```

where `[app-name]` is the directory where you want to place the migration ([`users`](/backend/users), [`workflows`](/backend/workflows), etc.).

Once the new migration is generated, you can either copy over the contents of an old waffle migration (like the pricing one linked above), _or_ (if you're using VSCode) simply generate the file with `migrateWaffle` snippet. Be sure to update the flag constant to the flag you defined in `flags.py`! Here you can also configure the initial availability or status of your feature flag (who it will be available to, etc.). By default, the flag will be disabled for everyone.

**🚨 Extremely Important:** It is of crucial importance that you take note of the dependency array, which will look something like this:

```python
dependencies = [
    ("users", "0071_auto_20220811_2128"),
]
```

The first tuple value will be the **app directory where you generated your migration**, where the second is the **previous migration in the migration directory**. This helps Django create a linear dependency chain of migrations, and if two migrations have the same dependency then it will cause the `migrate` command to fail. It is important to always check this if you are working on a feature branch and merge or rebase with `master`, as if new migrations are added and you don't update the dependency array of your migration, it will break. Note that we now have a mechanism to alert us when this happens: the latest migration's name will be save in a `latest_migrations/[app directory]` and there will be a merge conflict preventing the merge. See details in this [slack thread](https://basetenlabs.slack.com/archives/C014JUXFGLU/p1673454218916209).

Once your new migration file is added, just run `uv run manage.py migrate` to add it to your local database.

Once you've migrated in your new feature flag, it should be available via [/billip/waffle/flag](http://localhost:8000/billip/waffle/flag/).

## Using Feature Flags

### On the Frontend

Determining the status of a flag can be done like so:

```typescript
import { useCheckFeatureFlag } from '@/hooks/useFeatureFlags';
import { FeatureFlags } from '@/hooks/useFeatureFlags/types';

// ...
const checkFeatureFlag = useCheckFeatureFlag();
const isWorkletTestEnabled = checkFeatureFlag(FeatureFlags.WORKLET_TESTS_FLAG);
```

### On the Backend

```python
from feature_flags.flags import BINARY_INTERFACE
from feature_flags.services import get_flag_for_user
# ...
use_binary = get_flag_for_user(invoker, BINARY_INTERFACE)
```

## Deleting a feature flag

Removing a feature must be done in 2 steps to ensure a smooth transition adn no error while the django app is rotating:

1. Remove all usage of the feature flag from the code base, ensuring that the behavior that is left in the code base is the desired one. Open a PR for this code change and make sure it is deployed to production before moving on to the next step.
2. Create a database migration that delete the feature. This is the step where the constant from `feature_flags/flags.py` can be removed.
   - Note that when deleting the constant, you will need to go back to the migration that originally created the flag and replace the constant with its value. This is so past migrations can still be applied. See [this PR](https://github.com/basetenlabs/baseten/pull/2226/) for an example.
   - It is also a good idea to add a rollback method in the migration to ensure it is reversible. See [this migration](https://github.com/basetenlabs/baseten/blob/1ddaae801fab5078d8063a83e119b9fc7e3552ee/backend/oracles/migrations/0175_auto_20230205_2139.py) for an example
   - If you're removing a single flag, check which Django app (users, workflows, oracles, chains) the migration that added the flag lives in and create the cleanup migration there. If you're removing multiple flags at once, make sure to create cleanup migrations in the apps in which the flags were introduced. See [this PR](https://github.com/basetenlabs/baseten/pull/10720) for an example.
