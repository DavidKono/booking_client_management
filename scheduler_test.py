from concurrent import futures
import time
import grpc

import booking_pb2
import booking_pb2_grpc

SCHEDULER_ADDR = "localhost:8080"

class SchedulerServicer(booking_pb2_grpc.SchedulerServicer):
    def RequestJourney(self, request, context):
        now_unix = int(time.time())

        return booking_pb2.GetBookingResponse(
            booking_id="200",
            driver_id=request.driver_id,
            vehicle_id=request.vehicle_id,
            origin_node_id=request.origin_node_id,
            destination_node_id=request.destination_node_id,
            departure_time_unix=request.departure_time_unix,
            estimated_duration_s=request.estimated_duration_s,
            status=booking_pb2.CONFIRMED,
            jurisdiction_code=request.jurisdiction_code,
            route_id="route_1",
            created_at_unix=now_unix,
            expires_at_unix=now_unix + 300,
            version=1,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    booking_pb2_grpc.add_SchedulerServicer_to_server(
        SchedulerServicer(),
        server
    )

    server.add_insecure_port(SCHEDULER_ADDR)
    server.start()

    server.wait_for_termination()

if __name__ == "__main__":
    serve()