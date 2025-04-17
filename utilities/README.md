# Overview

This folder contains several utilities, such as bash scripts related to the project, including:

- `connect-db.sh` - connects to the PostgreSQL database for querying the database
- `load-mock-data.sh`- loads the mock data for example data in the dashboard
- `reset-db.sh` - resets the database

Both `load-mock-data.sh` and `reset-db.sh` must be run while inside this `utilities` directory.

# Pre-requisites:

- `connect-db.sh` requires a .env of format:
```
DB_USERNAME=
DB_PASSWORD=
DB_PORT=
DB_NAME=
DB_HOST=
```