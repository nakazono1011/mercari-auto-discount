#!/bin/bash

aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin 445217156642.dkr.ecr.ap-northeast-1.amazonaws.com

# Build image
docker build -t dev-sellin-selenium-server .

# Tag
docker tag dev-sellin-selenium-server:latest 445217156642.dkr.ecr.ap-northeast-1.amazonaws.com/dev-sellin-selenium-server:latest

# Push image
docker push 445217156642.dkr.ecr.ap-northeast-1.amazonaws.com/dev-sellin-selenium-server:latest