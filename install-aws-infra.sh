#!/bin/bash

while true; do
  output=$(clawhub install aws-infra 2>&1)
  echo "$output"
  if [[ "$output" != *"Rate limit exceeded"* ]]; then
    echo "Installation successful or other issue occurred. Exiting script."
    break
  fi
  echo "Rate limit exceeded. Trying again in 10 minutes."
  sleep 600
  # Sleep for 10 minutes

done