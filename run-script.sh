echo "running web scrapper..."
screen -S s1

Xvfb :99 -ac & DISPLAY=:99 python3 scrapper.py
