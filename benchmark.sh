#!/bin/bash

for i in {1..100}; do
  ./battleships.py --no-delay
  i="$?"
  total=$((total + i))
done
echo "$((total / 100))"
