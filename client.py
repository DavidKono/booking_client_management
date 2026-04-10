from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import grpc
import webbrowser
import threading
import time

import booking_pb2
import booking_pb2_grpc


GRPC_SERVER_ADDRESS = "localhost:10000"

app = FastAPI(title="Booking Client API")


class BookingInput(BaseModel):
    driver_id: str
    vehicle_id: str
    origin_node_id: int
    destination_node_id: int
    departure_time_unix: int
    estimated_duration_s: int
    jurisdiction_code: str

class CancelBookingInput(BaseModel):
    driver_id: str
    booking_id: str

@app.get("/")
def serve_index():
    return FileResponse("index.html")


@app.post("/submit-booking")
def submit_booking(data: BookingInput):
    try:
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
            stub = booking_pb2_grpc.ClientManagerStub(channel)

            response = stub.SubmitBooking(
                booking_pb2.CreateBookingRequest(
                    driver_id=data.driver_id,
                    vehicle_id=data.vehicle_id,
                    origin_node_id=data.origin_node_id,
                    destination_node_id=data.destination_node_id,
                    departure_time_unix=data.departure_time_unix,
                    estimated_duration_s=data.estimated_duration_s,
                    jurisdiction_code=data.jurisdiction_code,
                )
            )

        return {
            "booking_id": response.booking_id,
            "driver_id": response.driver_id,
            "vehicle_id": response.vehicle_id,
            "origin_node_id": response.origin_node_id,
            "destination_node_id": response.destination_node_id,
            "departure_time_unix": response.departure_time_unix,
            "estimated_duration_s": response.estimated_duration_s,
            "status": booking_pb2.BookingStatus.Name(response.status),
            "jurisdiction_code": response.jurisdiction_code,
            "route_id": response.route_id,
            "created_at_unix": response.created_at_unix,
            "expires_at_unix": response.expires_at_unix,
            "version": response.version,
        }

    except grpc.RpcError as e:
        return {
            "booking_id": "",
            "driver_id": data.driver_id,
            "vehicle_id": data.vehicle_id,
            "origin_node_id": data.origin_node_id,
            "destination_node_id": data.destination_node_id,
            "departure_time_unix": data.departure_time_unix,
            "estimated_duration_s": data.estimated_duration_s,
            "status": "ERROR",
            "jurisdiction_code": data.jurisdiction_code,
            "route_id": "",
            "created_at_unix": 0,
            "expires_at_unix": 0,
            "version": 0,
            "message": f"gRPC error: {e}",
        }

    except Exception as e:
        return {
            "booking_id": "",
            "driver_id": data.driver_id,
            "vehicle_id": data.vehicle_id,
            "origin_node_id": data.origin_node_id,
            "destination_node_id": data.destination_node_id,
            "departure_time_unix": data.departure_time_unix,
            "estimated_duration_s": data.estimated_duration_s,
            "status": "ERROR",
            "jurisdiction_code": data.jurisdiction_code,
            "route_id": "",
            "created_at_unix": 0,
            "expires_at_unix": 0,
            "version": 0,
            "message": f"Unexpected error: {e}",
        }
    
# @app.post("/cancel-booking")
# def cancel_booking(data: CancelBookingInput):
#     try:
#         with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
#             stub = booking_pb2_grpc.ClientManagerStub(channel)

#             response = stub.CancelBooking(
#                 booking_pb2.CancelBookingRequest(
#                     booking_id=data.booking_id,
#                     requesting_driver_id=data.booking_id,
#                 )
#             )

#         return {
#             "booking": response.booking,
#             "error_code": response.error_code,
#             "message": response.message,
#         }
#     except Exception as e:
#         return {

#         }
@app.post("/cancel-booking")
def cancel_booking(data: CancelBookingInput):
    try:
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
            stub = booking_pb2_grpc.ClientManagerStub(channel)

            response = stub.CancelBooking(
                booking_pb2.CancelBookingRequest(
                    booking_id=data.booking_id,
                    requesting_driver_id=data.driver_id,
                )
            )

        booking = response.booking

        return {
            "booking_id": booking.booking_id,
            "driver_id": booking.driver_id,
            "vehicle_id": booking.vehicle_id,
            "origin_node_id": booking.origin_node_id,
            "destination_node_id": booking.destination_node_id,
            "departure_time_unix": booking.departure_time_unix,
            "estimated_duration_s": booking.estimated_duration_s,
            "status": booking_pb2.BookingStatus.Name(booking.status),
            "jurisdiction_code": booking.jurisdiction_code,
            "route_id": booking.route_id,
            "created_at_unix": booking.created_at_unix,
            "expires_at_unix": booking.expires_at_unix,
            "version": booking.version,
            "error_code": response.error_code,
            "message": response.message,
        }

    except grpc.RpcError as e:
        return {
            "booking_id": data.booking_id,
            "driver_id": data.driver_id,
            "status": "ERROR",
            "message": f"gRPC error: {e}",
        }

    except Exception as e:
        return {
            "booking_id": data.booking_id,
            "driver_id": data.driver_id,
            "status": "ERROR",
            "message": f"Unexpected error: {e}",
        }

def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    import uvicorn

    threading.Thread(target=open_browser).start()

    uvicorn.run(
        "client:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )