# syntax=docker/dockerfile:1

# 1. tell Docker which base image to use
FROM python:3.8-slim-buster

# 2. tell Docker which folder to use for the rest of the operations
WORKDIR /narwhal-docker

# 3.1 tell docker to copy contents of the requirements file into the container image's requirements file
COPY requirements.txt requirements.txt
# 3.2 run pip install to install all the dependencies in the same file to be used by the image.
RUN pip3 install -r requirements.txt
# 3.3 we now copy the remainder of the files in our local working directory to the directory in the docker image
COPY . .

# 4. instructs Docker to run our Flask app as a module, as indicated by the "-m" tag. Then it instructs Docker to 
#    make the container available externally, such as from our browser, rather than just from within the container.
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]


# 1) In order for Docker to build images automatically, a set of instructions must be stored in 
#    a special file known as a Dockerfile. The instructions in this file are executed by the user 
#    on the command line interface in order to create an image.
#
# 2) A docker image, is a blueprint that specifies how to run an application. 
#
# 3) A docker container is a collection of dependencies and code organized as software that enables 
#    applications to run quickly and efficiently in a range of computing environments.