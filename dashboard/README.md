# Folder for dashboard / visualisations
This folder contains a Streamlit dashboard that loads data from the RDS using psycopg2.
To run locally: `streamlit run dashboard.py`.

# Requirements

To install requirements run:
`pip install -r requirements.txt`

A .env file must contain these variables:

```
DB_HOST=
DB_NAME=
DB_USERNAME=
DB_PASSWORD=
DB_PORT=
```


Dashboard Wireframe:
![Dashboard Wireframe](../assets/dashboard_wireframe.png)