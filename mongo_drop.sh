#!/bin/bash

# MongoDB shell commands to drop databases
mongo --eval "db.getSiblingDB('info').dropDatabase()"
mongo --eval "db.getSiblingDB('history').dropDatabase()"
mongo --eval "db.getSiblingDB('file').dropDatabase()"
