#!/usr/bin/env bash

gcc reader.c -lmosquitto -lcjson -lcurl -o reader
