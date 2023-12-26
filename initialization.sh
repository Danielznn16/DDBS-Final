mkdir -p ./ddbs_1_data
mkdir -p ./ddbs_2_data
docker-compose up -d
python3 bulk_load_data.py &
ocker exec -td ddbsNamenode bash -c 'hadoop fs -put /buffer/* /'
