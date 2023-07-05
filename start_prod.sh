docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
sleep 3
docker-compose exec web python manage.py migrate --noinput
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
