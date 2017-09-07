#!/bin/bash
while true
do
sudo python3 /home/pi/bot/bot.py

echo "¡The bot is crashed!"
echo "Rebooting in:"
for i in 1
do
echo "$i..."
done
echo "###########################################"
echo "#Bot is restarting now #"
echo "###########################################"
done