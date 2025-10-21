# Deployment orchestration gotchas
Due to the distributed nature of baseten application some changes need deployment orchestration. In general, 
it's good to be mindful of the distributed nature but it's worth calling out couple of common cases.

## Django database schema changes
Any db migrations for postgres db backing the Django app, roll out before the Django app itself. This means 
that old Django code would still be running for a bit after the migration is applied. So, care should be taken
to make sure that the existing Django can still work with the new state of the database after the migration.

For example, if a field needs to be removed from a table it would need two deploy.
1. Remove code in Django that accesses the field
2. Migration to remove the field


## Pynode <> Django interface

Pynodes take a long time to deploy, so they already run behind Django deploys by hours. Perhaps more importantly, 
we don't deploy pynodes for dormant orgs at all. When these dormant pynodes come back up on activity, they may end up running
old version of pynode infra code (the flask app, baseten_internal code and other helpers) for a few minutes, until
a fresh version is deployed. The pynode infra code in these pynodes may be up to a few weeks old. This can be an issue if/when
we introduce new interactions between django and pynode. In such cases:

1. Deploy the pynode side of change to all pynodes first. Either wait for the few weeks to pass, or force deploy the change on 
dormant pynodes. (todo: Add instructions for triggering the full pynode deploy job)
2. Deploy the django side of code.

## todo update this for tekton task/helm
