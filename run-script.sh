echo "running web scrapper..."
screen -S s1

Xvfb :99 -ac & DISPLAY=:99 python3 scrapper.py -i /home/sloppie/scrapper/migrator/viable_hotels_pictures_settings.json -e -it Photograph -is Large -ssf Strict
