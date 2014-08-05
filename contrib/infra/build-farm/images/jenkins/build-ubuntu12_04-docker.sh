#!/bin/bash

sudo docker build -t solum/jenkins:u1204 .
sudo docker tag solum/jenkins:u1204 solum/jenkins
