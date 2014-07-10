#!/bin/bash

sudo docker build -t solum/jenkins:u1304 .
sudo docker tag solum/jenkins:u1304 solum/jenkins
