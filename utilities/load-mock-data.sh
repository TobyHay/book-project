source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -p $DB_PORT -U $DB_USERNAME -d $DB_NAME -f ../database/mock_data.sql