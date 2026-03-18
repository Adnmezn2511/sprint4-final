source deploy.env
echo "REACT_APP_API_URL = http://$HOSTNAME:$PORT/api/" > frontend/.env.production
echo "PUBLIC_URL = http://$HOSTNAME:$PORT/static" >> frontend/.env.production
sudo docker compose --env-file deploy.env -f docker-compose.deploy.yml build --no-cache
sudo docker compose --env-file deploy.env -f docker-compose.deploy.yml up