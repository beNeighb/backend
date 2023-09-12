docker-compose -f docker-compose.yml down -v

images=$(docker images -q)
docker rmi -f $images

docker-compose -f docker-compose.yml up -d
sleep 3
docker-compose exec web python manage.py migrate --noinput
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear
