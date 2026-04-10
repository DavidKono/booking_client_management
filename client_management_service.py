from concurrent import futures
import time
import grpc

import booking_pb2
import booking_pb2_grpc
import scheduler_pb2
import scheduler_pb2_grpc

CLIENT_MANAGEMENT_ADDR = "0.0.0.0:10000"
SCHEDULER_ADDR = "localhost:8080"

class ClientManagerServicer(booking_pb2_grpc.ClientManagerServicer):
    def SubmitBooking(self, request, context):
        try:
            with grpc.insecure_channel(SCHEDULER_ADDR) as channel:
                scheduler_stub = scheduler_pb2_grpc.SchedulerServiceStub(channel)

                scheduler_response = scheduler_stub.CreateBooking(
                    scheduler_pb2.CreateBookingRequest(
                        driver_id=request.driver_id,
                        vehicle_id=request.vehicle_id,
                        origin_node_id=request.origin_node_id,
                        destination_node_id=request.destination_node_id,
                        departure_time_unix=request.departure_time_unix,
                        estimated_duration_s=request.estimated_duration_s,
                        jurisdiction_code=request.jurisdiction_code,
                    )
                )

                return scheduler_response.booking

        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(
                f"Failed to contact Scheduler at {SCHEDULER_ADDR}: {e.details() or str(e)}"
            )

            now_unix = int(time.time())

            return booking_pb2.GetBookingResponse(
                booking_id="",
                driver_id=request.driver_id,
                vehicle_id=request.vehicle_id,
                origin_node_id=request.origin_node_id,
                destination_node_id=request.destination_node_id,
                departure_time_unix=request.departure_time_unix,
                estimated_duration_s=request.estimated_duration_s,
                status=booking_pb2.DENIED,
                jurisdiction_code=request.jurisdiction_code,
                route_id="",
                created_at_unix=now_unix,
                expires_at_unix=0,
                version=1,
            )
    def CancelBooking(self, request, context):
        try:
            with grpc.insecure_channel(SCHEDULER_ADDR) as channel:
                scheduler_stub = scheduler_pb2_grpc.SchedulerServiceStub(channel)

                scheduler_response = scheduler_stub.CancelBooking(
                    scheduler_pb2.CancelBookingRequest(
                        booking_id=request.booking_id,
                        requesting_driver_id=request.requesting_driver_id,
                    )
                )

                booking = scheduler_response.booking

                return booking_pb2.CancelBookingResponse(
                    booking=booking_pb2.GetBookingResponse(
                        booking_id=booking.booking_id,
                        driver_id=booking.driver_id,
                        vehicle_id=booking.vehicle_id,
                        origin_node_id=booking.origin_node_id,
                        destination_node_id=booking.destination_node_id,
                        departure_time_unix=booking.departure_time_unix,
                        estimated_duration_s=booking.estimated_duration_s,
                        status=booking.status,
                        jurisdiction_code=booking.jurisdiction_code,
                        route_id=booking.route_id,
                        created_at_unix=booking.created_at_unix,
                        expires_at_unix=booking.expires_at_unix,
                        version=booking.version,
                    ),
                    error_code=scheduler_response.error_code,
                    message=scheduler_response.message,
                )

        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(
                f"Failed to contact Scheduler at {SCHEDULER_ADDR}: {e.details() or str(e)}"
            )

            now_unix = int(time.time())

            return booking_pb2.CancelBookingResponse(
                booking=booking_pb2.GetBookingResponse(
                    booking_id=request.booking_id,
                    driver_id="",
                    vehicle_id="",
                    origin_node_id=0,
                    destination_node_id=0,
                    departure_time_unix=0,
                    estimated_duration_s=0,
                    status=booking_pb2.DENIED,
                    jurisdiction_code="",
                    route_id="",
                    created_at_unix=now_unix,
                    expires_at_unix=0,
                    version=0,
                ),
                error_code="UNAVAILABLE",
                message=f"Failed to contact Scheduler at {SCHEDULER_ADDR}: {e.details() or str(e)}",
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    booking_pb2_grpc.add_ClientManagerServicer_to_server(
        ClientManagerServicer(),
        server
    )

    server.add_insecure_port(CLIENT_MANAGEMENT_ADDR)
    server.start()

    server.wait_for_termination()

if __name__ == "__main__":
    serve()