
# JSON API (BCO API)

This is the repository for the BioCompute Objects API.  Architecturally, the API is separated from any BCO interface (BioCompute Portal, Galaxy, GlyGen, etc...) and can be used with the standard POST, GET, PATCH, and DELETE commands.  The repository comes with an out-of-the-box security policy and can be used within an organization's firewall without much further configuration on the part of the administrator.

# Overview of Repository Contents

The API is built on Django.  Initial setup only involves modifying a few settings and for most users the default security settings should suffice.  The exception to this is the case where an administrator wants their BCOs to be public-facing.  **The server is not secured with any type of API key system!**  If you want to add additional security features you will have to go through the source code and decide what is necessary for your specific installation.  Only files that have been modified or created in addition to the default files of a Django installation are described here.

## Folder Description

```
API
 └─── api (contains the heart of the API)
    └─── library (class definitions)
       └─── DbUtils.py (class for interacting with the SQLite database)
       └─── JsonUtils.py (class for validating JSON)
       └─── RequestUtils.py (class for dealing with requests)
       └─── ResponseUtils.py (class for dealing with responses given by the API)
    └─── request_definitions (schema definitions for each type of request to the API)
       └─── DELETE.schema (the schema definition for a valid DELETE request)
       └─── GET.schema (the schema definition for a valid GET request)
       └─── PATCH.schema (the schema definition for a valid PATCH request)
       └─── POST.schema (the schema definition for a valid POST request)
    └─── validation_definitions* (schema definitions for each type of non-URI validation request)
 └─── api_master (contains top-level project settings)
    └─── settings.py* (where settings such as default object naming and schema registration take place)
    └─── urls.py* (pass-through router to the API urls file)
```

\* These files are the only ones that should be manually edited, if at all.

# Quick Start

1.  Clone the repository.  If necessary, add execute permissions to all shell scripts.

```
git clone https://github.com/carmstrong1gw/bco_api
(optional, add execute permissions) sudo some grep commmand +x...
```

2.  Initialize the folder contents (creates virtual environment and adjusts some settings).  At the end of this step, your command line should show an active virtual environment.

```
initialize_api.sh
(should see this after running initialize_api.sh) (env) user@computer:/path/to/json_api$
```

3.  Create a super user (administrator).  Fill in all details as necessary.

```
python3 manage.py createsuperuser
```

4.  Start the server with the shell script

```
start_server.sh
```

5.  Open up your browser and go to https://127.0.0.1/8000/admin

6.  Right now the only user is the administrator


