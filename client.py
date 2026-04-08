from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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
    username: str
    origin: str
    destination: str
    departure_time: str

# serve index.html
@app.get("/")
def serve_index():
    return FileResponse("index.html")


@app.post("/submit-booking")
def submit_booking(data: BookingInput):
    try:
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
            stub = booking_pb2_grpc.ClientManagerStub(channel)

            response = stub.SubmitBooking(
                booking_pb2.BookingRequest(
                    username=data.username,
                    origin=data.origin,
                    destination=data.destination,
                    departure_time=data.departure_time,
                )
            )

        return {
            "accepted": response.accepted,
            "booking_id": response.booking_id,
            "message": response.message,
        }

    except grpc.RpcError as e:
        return {
            "accepted": False,
            "booking_id": "",
            "message": f"gRPC error: {e}",
        }
    except Exception as e:
        return {
            "accepted": False,
            "booking_id": "",
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