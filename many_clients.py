import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import grpc

import booking_pb2
import booking_pb2_grpc


ADDR = "localhost:10000"


def send_request(i: int):
    with grpc.insecure_channel(ADDR) as channel:
        stub = booking_pb2_grpc.ClientManagerStub(channel)

        response = stub.SubmitBooking(
            booking_pb2.CreateBookingRequest(
                driver_id=f"driver_{i}",
                vehicle_id="CAR1",
                origin_node_id=1,
                destination_node_id=2,
                departure_time_unix=int(time.time()) + i*3600,
                estimated_duration_s=1800,
                jurisdiction_code="IE",
            )
        )
        return i, response


def main():
    num_clients = 100

    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [executor.submit(send_request, i) for i in range(num_clients)]

        for future in as_completed(futures):
            i, response = future.result()
            print(f"Client {i}: booking_id={response.booking_id}, status={response.status}")


if __name__ == "__main__":
    main()