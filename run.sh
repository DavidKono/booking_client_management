python3 -m venv venv
source venv/bin/activate

pip3 install -r reqs.txt

python3 -m grpc_tools.protoc -I. \
  --python_out=. \
  --grpc_python_out=. \
  booking.proto

python3 -m grpc_tools.protoc -I. \
  --python_out=. \
  --grpc_python_out=. \
  scheduler.proto

python3 client_management_service.py &
PID1=$!
python3 client.py &
PID2=$!

# properly kill server
trap "kill $PID1 $PID2; exit" INT
wait