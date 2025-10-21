# Generating a SQL Dump

If backend unit tests are getting slow again, the mechanism for re-creating a checkpoint is:
- Recreate a clean `baseten_test` database by running all our migrations from scratch.
- Generate a dump of the database state, both schema + data:
```
$ pg_dump --column-inserts -O --file=generated/sql/backend_db_dump_<date>.sql baseten_test -h <pg-host> -p <pg-port> -U baseten_test
```
- Update the [path](https://github.com/basetenlabs/baseten/blob/90c3b4439b795d63d6784d86d3679906c320bbad/backend/conftest.py?plain=1#L207) in our test settings
- Remove any old checkpoints that are no longer needed
