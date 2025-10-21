# How to connect to UDM DB

Connecting to UDM DB can be necassary when tryin got debug an issue to fix a wrong migration. There are two ways to connect to the UDM database: using customer credentials and using admin credentials.

## Connect using customer credentials
This method should be the preferred method when connecting directly to the UDM database. Those credentials are restricted to the database of the specific customer and cannot modify the schema.

1. Open a shell in a pod with the django settings (either a django or celery pod)
2. Get the UDM credentials for the desired customer.
    1. Open a `shell_plus`
    2. ```python
        org = Organization.objects.get(name="baseten")
        org.current_udm_credentials.host
        org.current_udm_credentials.db_name
        org.current_udm_credentials.db_user
        org.current_udm_credentials.password
       ```
3. Log into the UDM DB using `psql`
    1. `psql -h [host] -U [db_user] -d [db_name] -W`
    2. Enter the password when prompted
4. Switch to the correct schema (draft or production)
    1. `\dn` to list the schema
    2. `SET search_path TO '[schema]';`

## Connect using the admin credentials
This method should be used carefully, as this user has superuser permission in the UDM DB cluster.

1. Open a shell in a pod with the django settings (either a django or celery pod)
2. Get the admin credentials. They are located in the envrionment variable
    1. ```sh
        echo $UDM_DB_HOST
        echo $UDM_DB_NAME
        echo $UDM_DB_USER
        echo $UDM_DB_PASSWORD
       ```
3. Log into the UDM DB using `psql`
    1. `psql -h [host] -U [db_user] -d [db_name] -W`
    2. Enter the password when prompted
4. Switch to the correct database and schema (draft or production)
    1. `\l` to list the databases
    2. `\c [db_name]` to switch the connection to the desired database
    3. `\dn` to list the schema
    4. `SET search_path TO '[schema]';`
