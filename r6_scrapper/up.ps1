if($(docker ps -q)) {
    echo "Stopping containers..."
    docker rm -f -v $(docker ps -q)
    echo "Stopped!"
    echo ""

}

docker-compose --env-file env up --build -d

echo ""

docker ps
