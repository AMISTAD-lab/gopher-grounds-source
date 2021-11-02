for i in {1..10}; do screen -dmS "generate-ur-$i" python3 generateUR.py $i -g 8000800; done
