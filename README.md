# JarJar
A bot to do my groceries. Connects to monoprix.fr, schedule a delivery, fills the basket with all items in the last 2 orders, to avoid having to use the awful, very slow UX of the site (e.g. click on each item of last orders 1 by 1 and wait 10s in between). The only thing left to do is having to click on the order button in the end after reviewing the basket.

## Deprecation
The bot is not useful anymore since efficient online groceries solutions appeared (Monoprix itself is available as a grocery store on Amazon). Furthermore, the code uses selenium and a ghost chrome to emulate a real user -- it does not work any more since Monoprix revamped their website.

# Setup
After the git clone, in the repo dir :
```
sudo apt-get install xvfb
pip -r requirements.txt
xvfb-run --server-args='-screen 0, 1024x768x16' chromedriver
python fais_mes_courses.py
```
Line 3 runs a headless chrome as a server, that selenium can operate on port 9515 (default at time of writing).

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
