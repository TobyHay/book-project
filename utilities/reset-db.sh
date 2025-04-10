source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME -f ../database/schema.sql

if [ $? -eq 0 ]; then
  echo "Database successfully reset"
else
  echo "Failed to reset database"
fi