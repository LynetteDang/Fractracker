# update_docker_image.sh
# Utility file to update docker image on Google Cloud Container Registry after a 
# code update

docker-compose build
docker tag fractracker-complaints_fractracker gcr.io/fractracker/fractracker-complaints_fractracker
docker push gcr.io/fractracker/fractracker-complaints_fractracker

# Remove dangling (non- "latest") images
docker rmi -f $(docker images -f "dangling=true" -q)
