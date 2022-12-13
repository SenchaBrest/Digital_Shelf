#for i in {1..47}
#do
#    python3 detect.py --weights 3.pt 4.pt 5.pt 6.pt --conf 0.80 --img-size 640  --source valid-objects/$i.jpg --save-txt
#done
cd products_pkl
for i in {1..12}
do
    cd $i
    rm *.jpg
    cd ..
done