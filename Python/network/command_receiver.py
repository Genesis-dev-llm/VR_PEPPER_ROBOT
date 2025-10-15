import asyncio
import websockets
import json

class CommandReceiver:
    """
    Handles the WebSocket server. Its ONLY job is to listen for incoming messages,
    parse them as JSON, and pass them to the main PepperController for processing.
    It is completely decoupled from the robot's actual logic.
    """
    def __init__(self, pepper_controller, host, port):
        self.pepper = pepper_controller
        self.host = host
        self.port = port

    async def handler(self, websocket, path):
        """A new handler is created for each connected Unity client."""
        print(f"Unity client connected from {websocket.remote_address}")
        try:
            # Listen for messages indefinitely
            async for message in websocket:
                try:
                    command = json.loads(message)
                    # This is the key connection point:
                    # Pass the validated command to the central controller.
                    self.pepper.process_command(command)
                except Exception as e:
                    print(f"Error processing command: {e}")
        except websockets.exceptions.ConnectionClosed:
            print(f"Unity client disconnected.")
        finally:
            # Safety feature: If the connection drops, stop the robot.
            self.pepper.emergency_stop()

    async def start(self):
        """Starts the WebSocket server and waits forever."""
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future() # Run forever