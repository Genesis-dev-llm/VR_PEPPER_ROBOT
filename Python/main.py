import argparse
import asyncio
import threading
from network.command_receiver import CommandReceiver
from network.video_streamer import VideoStreamer
from pepper_control.pepper_controller import PepperController

# --- GLOBAL CONFIGURATION ---
# These are the default values for the server.
DEFAULT_ROBOT_IP = "192.168.1.100" # A placeholder IP
ROBOT_PORT = 9559
COMMAND_PORT = 5000
VIDEO_PORT = 8080

def start_video_stream(ip, port):
    """
    This function is designed to run in a separate thread.
    It creates and starts the Flask video streaming server.
    """
    try:
        video_streamer = VideoStreamer(ip, port)
        video_streamer.run(host='0.0.0.0', port=VIDEO_PORT)
    except Exception as e:
        print(f"\033[91mVideo streaming thread failed: {e}\033[0m")

async def main(robot_ip):
    """
    The main asynchronous function that orchestrates the application startup.
    """
    print(f"--- Pepper VR Teleoperation Server ---")
    
    try:
        # 1. Initialize the main Pepper controller (the "brain")
        print(f"Attempting to connect to Pepper at {robot_ip}:{ROBOT_PORT}...")
        pepper_controller = PepperController(robot_ip, ROBOT_PORT)
        print("✓ Successfully connected to Pepper.")
        
        # 2. Start the video streamer in a background thread.
        #    We use a thread because Flask is not an asyncio-native library.
        #    'daemon=True' ensures the thread will exit when the main program does.
        video_thread = threading.Thread(
            target=start_video_stream, 
            args=(robot_ip, ROBOT_PORT),
            daemon=True
        )
        video_thread.start()
        
        # 3. Start the WebSocket server for commands. This will run in the
        #    main asyncio loop and wait for Unity to connect.
        command_server = CommandReceiver(pepper_controller, '0.0.0.0', COMMAND_PORT)
        print(f"✓ Starting command server on WebSocket port {COMMAND_PORT}...")
        await command_server.start()
        
    except Exception as e:
        print(f"\033[91mFATAL ERROR during startup: {e}\033[0m")
        print("Please check Pepper's IP address, network connection, and ensure NAOqi is running.")

if __name__ == "__main__":
    # This block handles command-line arguments, allowing you to specify
    # the robot's IP when you run the script.
    parser = argparse.ArgumentParser(description="Run the Pepper VR Teleoperation Server.")
    parser.add_argument(
        '--ip', 
        type=str, 
        default=DEFAULT_ROBOT_IP, 
        help=f"The IP address of the Pepper robot. Defaults to {DEFAULT_ROBOT_IP}."
    )
    args = parser.parse_args()

    try:
        # Start the main asyncio event loop
        asyncio.run(main(args.ip))
    except KeyboardInterrupt:
        # This allows you to shut down the server gracefully with Ctrl+C
        print("\nServer shutting down.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")