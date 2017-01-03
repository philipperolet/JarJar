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
*j. that actually fills your basket & returns missing items

- that is dockerized
- that is apized
- that is chatbotted

## Icebox
### Refactoring
- check private methods
- separate monop api (not testable) with monop bot (testable with api as input)

### Filling the basket
- add test to check that item is not added if already present in basket

# Development notes
## Testablility
The code mixes 2 things :
- a layer on top of selenium mapping monoprix site ux to an "API"
- a bot logic using this api

While the first one is hardly unit testable (just mapping api methods to site user actions), the second one should be tested.

Having a real stateless API is kind of impractical, notably because:
- atomicity of actions would require lots of ghost browsing;
- impossible to add a single item easily

So at the time both are a bit mixed; it's mostly an api and not much tested.
