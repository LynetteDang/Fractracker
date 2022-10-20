# run.sh
#
# Builds and runs a Docker container with Selenium and 
# Chromedriver installed and then enables an interactive
# bash terminal from which users can view container contents
# and execute Python scripts. Mounts the entire code
# directory to permit testing without container restarts.
# 

# Define variables
IMAGE_NAME=fractracker
CONTAINER_NAME=fractracker-app
CONTAINER_DIRECTORY=fractracker-complaints

# Start Docker container
docker-compose run --name $CONTAINER_NAME \
    -v "/${PWD}:/${CONTAINER_DIRECTORY}" \
    -p 8080:8080 \
    --rm $IMAGE_NAME 
