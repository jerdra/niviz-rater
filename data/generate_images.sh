count=0
while read p; do
  echo $p
  count=$((count+=25))
  wget -O $2/$p.png https://picsum.photos/id/$count/500/300
done < $1
