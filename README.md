# JarJar
A bot to do my groceries.

## Setup
After the git clone, in the repo dir :
`sudo apt-get install xvfb
pip -r requirements.txt
xvfb-run --server-args='-screen 0, 1024x768x16' chromedriver
python fais_mes_courses.py
`
Line 3 runs a headless chrome as a server, that selenium can operate on port 9515 (default at time of writing).

## Ongoing todo
1. A script
a. that says hello world
b. that reads the monoprix page title
c. that clicks on MonCompte
d. that logs in
e. that displays an info about amount of last order
f. that waits correclty before logging
g. that's headless
h. that logs what's going on
i. that sets up the delivery time
--> between day n+1 at noon and day n+5 included
--> between 7 and 21 with round hour
--> at an available date
*j. that actually fills your basket & co

- that is dockerized
- that is apized
- that is chatbotted




