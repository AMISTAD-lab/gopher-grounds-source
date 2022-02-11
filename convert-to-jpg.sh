for i in $(ls . | cut -f1 -d'.'); do convert "$i.pdf" "../vectors/$i.jpg"; done;
