from concurrent import futures
import grpc

import booking_pb2
import booking_pb2_grpc

class ClientManagerServicer(booking_pb2_grpc.ClientManagerServicer):
    def SubmitBooking(self, request, context):
        print("Received booking request:")
        print(f"    username: {request.username}")
        print(f"    origin: {request.origin}")
        print(f"    destination: {request.destination}")
        print(f"    departure_time: {request.departure_time}")

        # mock id
        booking_id = str(1000)

        return booking_pb2.BookingReply(
            accepted=True,
            booking_id=booking_id,
            message=f"Booking accepted for {request.username}"
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