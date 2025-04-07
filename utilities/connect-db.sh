source .env
export PGPASSWORD=$PGPASSWORD
psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME
