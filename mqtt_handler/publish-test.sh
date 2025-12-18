#!/usr/bin/env bash

mosquitto_pub -h 127.0.0.1 -t messages -m '{"temperature":25.234, "pressure":1000.433, "humidity":87.343, "rain":1}' 
