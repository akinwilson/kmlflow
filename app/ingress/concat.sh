#!/bin/bash

# Check if at least one file is provided as an argument
if [ $# -eq 0 ]; then
  echo "Usage: $0 file1.yaml file2.yaml ..."
  exit 1
fi

# Output file
output_file="total.yaml"

# Clear the output file if it already exists
> "$output_file"

# Loop through each file provided as an argument
for file in "$@"; do
  # Check if the file exists
  if [ ! -f "$file" ]; then
    echo "Error: File '$file' not found!"
    exit 1
  fi

  # Append the content of the file to the output file
  cat "$file" >> "$output_file"

  # Append '---' separator unless it's the last file
  if [ "$file" != "${@: -1}" ]; then
    echo "---" >> "$output_file"
  fi
done

echo "Concatenated YAML files into $output_file"
