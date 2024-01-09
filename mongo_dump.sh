#!/bin/bash

# Directory where dumps will be stored
DUMP_DIR="/data_load/dumps"

# Create the dump directory if it doesn't exist
mkdir -p "$DUMP_DIR"

rm -rf "$DUMP_DIR/*"

# Dump the databases
mongodump --db info --out "$DUMP_DIR"
mongodump --db history --out "$DUMP_DIR"
mongodump --db file --out "$DUMP_DIR"
