#!/bin/bash

# Directory where dumps are stored
DUMP_DIR="/data_load/dumps"

# Restore the databases
mongorestore "$DUMP_DIR"
