#  Build and run auction keeper as Docker image
## Prerequisite:
- docker installed: https://docs.docker.com/install/
- docker-compose: https://docs.docker.com/compose/install/
- Git

## Installation and build
#### Installation:
Clone project and install required third-party packages:
```
git clone https://github.com/monolithos/auction-keeper.git
cd auction-keeper
```

#### Build:
In `auction-keeper` directory:

- run `docker-compose build`

## Get image from DockerHub
 - run `docker pull monolithos/auction-keeper_keeper`

## RUN keeper:
- run 
```
    docker run --name "CONTAINER_NAME" --rm monolithos/auction-keeper_keeper \
           --model-start-percent 10 \
           --model-finish-percent 50 \
           --model-markup_percent 3 \
           --model-pair ETHRUB  \
           --model-our-address ADDRESS \
           --model-modal-type FLIP \
           -t flip \
           -h http://localhos:8545 \
           -i ETH-A \
           --network kovan \
           -a 0xC0CCab7430aEc0C30E76e1dA596263C3bdD82932 \
       -pk 0x874FE5759060000DEM0000DEM00000000000000000E2E1E37CD525F2009A79F8 \
````

