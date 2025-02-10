#!/bin/bash

# ASCII art for the text display
ASCII_ART="
 _              _  __ _               
| | ___ __ ___ | |/ _| | _____      __
| |/ / '_ \` _ \| | |_| |/ _ \ \ /\ / /
|   <| | | | | | |  _| | (_) \ V  V / 
|_|\_\_| |_| |_|_|_| |_|\___/ \_/\_/  
"
# # Progressive reveal from left to right
# animate_progressive_reveal() {
#   local width=$(tput cols)
#   for (( i = 0; i < ${#ASCII_ART}; i++ )); do
#     clear
#     # Print the characters progressively from left to right
#     echo -n "${ASCII_ART:0:i+1}"
#     sleep 0.005  # Adjust speed of progressive reveal
#   done
#   echo
# }
# 
# animate_progressive_reveal
# 



# Bounce vertically from top to bottom
animate_vertical_bounce() {
  for (( i = 0; i < ${#ASCII_ART}; i++ )); do
    clear
    # Print each character progressively with some vertical movement
    echo -n "${ASCII_ART:0:i+1}"
    sleep 0.005
  done
  echo
}

animate_vertical_bounce



# # Function to animate the ASCII art moving onto the screen
# animate_ascii_art() {
#   # Iterate through each character in the ASCII art
#   length=${#ASCII_ART}
#   
#   # Print one character at a time with a small delay
#   for (( i = 1; i <= length; i++ )); do
#     clear
#     # Print the first i characters of the ASCII art
#     echo -n "${ASCII_ART:0:i}"
#     sleep 0.005  # Adjust speed of animation (change sleep to make it faster or slower)
#   done
# }
# 
# # Call the function
# animate_ascii_art
# 
# Add the final message after the animation is complete


echo -e "\nYou have all CLI tools required, ready for local deployment of kmlflow"

