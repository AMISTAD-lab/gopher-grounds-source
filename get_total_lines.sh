export sum=0
for i in {1..120}; do
    temp=$(wc -l "uniform-random/uniform-random_new_enc_$i.csv" | cut -d" " -f1)
    sum=$(expr $sum + $temp)
done
