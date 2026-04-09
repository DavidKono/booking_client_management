from concurrent import futures
import time
import grpc

import booking_pb2
import booking_pb2_grpc


class ClientManagerServicer(booking_pb2_grpc.ClientManagerServicer):
    def SubmitBooking(self, request, context):
        now_unix = int(time.time())
        expires_at_unix = now_unix + 300  # mocked expiry in 5 mins
        booking_id = "1000"  # mocked id

        return booking_pb2.GetBookingResponse(
            booking_id=booking_id,
            driver_id=request.driver_id,
            vehicle_id=request.vehicle_id,
            origin_node_id=request.origin_node_id,
            destination_node_id=request.destination_node_id,
            departure_time_unix=request.departure_time_unix,
            estimated_duration_s=request.estimated_duration_s,
            status=booking_pb2.CONFIRMED,
            jurisdiction_code=request.jurisdiction_code,
            route_id="",
            created_at_unix=now_unix,
            expires_at_unix=expires_at_unix,
            version=1,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    booking_pb2_grpc.add_ClientManagerServicer_to_server(
        ClientManagerServicer(),
        server
    )

    port = "10000"
    server.add_insecure_port(f"[::]:{port}")
    server.start()

    print(f"ClientManager gRPC server listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()