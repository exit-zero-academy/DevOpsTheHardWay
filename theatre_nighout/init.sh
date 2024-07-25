rm -f -r shows

for i in 'The Lion King' 'Hamilton' 'Wicked' 'Les Miserables' 'Phantom of the Opera'
do
  mkdir -p shows/"$i"
  for j in $(seq 1 50)
  do
    touch shows/"$i"/"$j"
  done
done