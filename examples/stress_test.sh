#!/bin/bash

# Check if the model_tag argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <model_tag>"
  exit 1
fi

# Model tag (provided as an argument)
model_tag=$1

# Fixed duration for the loop (10 seconds)
end_time=$((SECONDS + 10))

# List of questions (embedded in the script)
questions=(
  "What is the capital of Japan?"
  "How does blockchain work?"
  "Why is climate change important?"
  "Can you explain the concept of quantum computing?"
  "What are the benefits of renewable energy?"
  "How do you solve the problem of cybersecurity?"
  "What is the purpose of the Internet?"
  "Who invented the light bulb?"
  "What are the main features of Python?"
  "How can I improve my skills in public speaking?"
  "What is the history of World War II?"
  "What are the challenges of the healthcare industry?"
  "How does machine learning affect data science?"
  "What is the difference between AI and robotics?"
  "What are the best practices for project management?"
  "How do you measure customer satisfaction?"
  "What are the risks of space exploration?"
  "What is the future of neuroscience?"
  "How do you implement agile methodology?"
  "What are the key components of cloud computing?"
  "What is the capital of France?"
  "How does quantum computing work?"
  "Why is space exploration important?"
  "Can you explain the concept of genetics?"
  "What are the benefits of programming?"
  "How do you solve the problem of time management?"
  "What is the purpose of the smartphone?"
  "Who invented the printing press?"
  "What are the main features of JavaScript?"
  "How can I improve my skills in cooking?"
  "What is the history of the Industrial Revolution?"
  "What are the challenges of the software development industry?"
  "How does cloud computing affect productivity?"
  "What is the difference between sustainability and globalization?"
  "What are the best practices for marketing?"
  "How do you measure employee engagement?"
  "What are the risks of digital transformation?"
  "What is the future of innovation?"
  "How do you implement software development?"
  "What are the key components of agile methodology?"
  "What is the capital of Brazil?"
  "How does machine learning work?"
  "Why is renewable energy important?"
  "Can you explain the concept of neuroscience?"
  "What are the benefits of photography?"
  "How do you solve the problem of financial performance?"
  "What is the purpose of the printing press?"
  "Who invented the Internet?"
  "What are the main features of cybersecurity?"
  "How can I improve my skills in time management?"
  "What is the history of the Renaissance?"
  "What are the challenges of the marketing industry?"
  "How does blockchain affect customer satisfaction?"
  "What is the difference between quantum computing and AI?"
  "What are the best practices for software development?"
  "How do you measure productivity?"
  "What are the risks of globalization?"
  "What is the future of sustainability?"
  "How do you implement project management?"
  "What are the key components of digital transformation?"
  "What is the capital of Australia?"
  "How does AI work?"
  "Why is genetics important?"
  "Can you explain the concept of space exploration?"
  "What are the benefits of public speaking?"
  "How do you solve the problem of employee engagement?"
  "What is the purpose of the light bulb?"
  "Who invented the smartphone?"
  "What are the main features of cloud computing?"
  "How can I improve my skills in photography?"
  "What is the history of COVID-19?"
  "What are the challenges of the robotics industry?"
  "How does Python affect innovation?"
  "What is the difference between machine learning and data science?"
  "What are the best practices for agile methodology?"
  "How do you measure financial performance?"
  "What are the risks of neuroscience?"
  "What is the future of quantum computing?"
  "How do you implement cybersecurity?"
  "What are the key components of blockchain?"
  "What is the capital of Canada?"
  "How does cybersecurity work?"
  "Why is the Industrial Revolution important?"
  "Can you explain the concept of climate change?"
  "What are the benefits of cooking?"
  "How do you solve the problem of customer satisfaction?"
  "What is the purpose of the Renaissance?"
  "Who invented the printing press?"
  "What are the main features of data science?"
  "How can I improve my skills in programming?"
  "What is the history of the light bulb?"
  "What are the challenges of the photography industry?"
  "How does renewable energy affect sustainability?"
  "What is the difference between blockchain and quantum computing?"
  "What are the best practices for digital transformation?"
  "How do you measure innovation?"
  "What are the risks of space exploration?"
  "What is the future of genetics?"
  "How do you implement machine learning?"
  "What are the key components of Python?"
  "What is the capital of Germany?"
  "How does robotics work?"
  "Why is the Renaissance important?"
  "Can you explain the concept of the Industrial Revolution?"
  "What are the benefits of time management?"
  "How do you solve the problem of productivity?"
  "What is the purpose of the printing press?"
  "Who invented the Internet?"
  "What are the main features of JavaScript?"
  "How can I improve my skills in public speaking?"
  "What is the history of World War II?"
  "What are the challenges of the healthcare industry?"
  "How does machine learning affect data science?"
  "What is the difference between AI and robotics?"
  "What are the best practices for project management?"
  "How do you measure customer satisfaction?"
  "What are the risks of space exploration?"
  "What is the future of neuroscience?"
  "How do you implement agile methodology?"
  "What are the key components of cloud computing?"
)

# Loop for 10 seconds
while [ $SECONDS -lt $end_time ]; do
  # Iterate over each question and send the curl request
  for question in "${questions[@]}"; do
    curl -X 'POST' \
      "http://192.168.49.2/$model_tag/v2/models/$model_tag/infer" \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
        "question": "'"$question"'"
      }'
    echo "" # Add a newline for better readability
  done
done