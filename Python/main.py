import argparse
import asyncio
import threading
import logging
import signal
import sys
from network.command_receiver import CommandReceiver
from network.video_streamer import VideoStreamer
from pepper_control.pepper_controller import PepperController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pepper_vr_server.log')
    ]
)
logger = logging.getLogger(__name__)

# Global configuration
DEFAULT_ROBOT_IP = "192.168.1.100"
ROBOT_PORT = 9559
COMMAND_PORT = 5000
VIDEO_PORT = 8080

# Global references for cleanup
pepper_controller = None
command_server = None
video_thread = None
shutdown_event = threading.Event()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("\n🛑 Shutdown signal received (Ctrl+C)")
    shutdown_event.set()
    
    if pepper_controller:
        pepper_controller.emergency_stop()
        pepper_controller.close()
    
    logger.info("Server stopped cleanly")
    sys.exit(0)

def start_video_stream(ip, port):
    """
    Video streaming thread function.
    Runs Flask server in a separate thread.
    """
    try:
        logger.info("Initializing video streamer...")
        video_streamer = VideoStreamer(ip, port)
        
        # Run Flask (blocks until server stops)
        video_streamer.run(host='0.0.0.0', port=VIDEO_PORT)
        
    except KeyboardInterrupt:
        logger.info("Video streaming thread interrupted")
    except Exception as e:
        logger.error(f"Video streaming thread failed: {e}", exc_info=True)

async def health_check_loop(pepper_ctrl):
    """
    Periodic health check of robot status.
    Runs in the background and logs warnings if issues detected.
    """
    logger.info("Starting health check loop...")
    
    while not shutdown_event.is_set():
        try:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            status = pepper_ctrl.get_robot_status()
            if status:
                battery = status.get('battery', 'Unknown')
                logger.info(f"Health Check - Battery: {battery}%")
                
                # Warn if battery low
                if isinstance(battery, (int, float)) and battery < 20:
                    logger.warning(f"⚠️  LOW BATTERY: {battery}%")
                    
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {e}")

async def main(robot_ip):
    """
    Main asynchronous function that orchestrates the application startup.
    """
    global pepper_controller, command_server, video_thread
    
    logger.info("╔════════════════════════════════════════════════════════╗")
    logger.info("║   Pepper VR Teleoperation Server - qi Framework       ║")
    logger.info("║   Version 1.0.0                                        ║")
    logger.info("╚════════════════════════════════════════════════════════╝")
    logger.info("")
    
    try:
        # 1. Initialize the main Pepper controller
        logger.info(f"Attempting to connect to Pepper at {robot_ip}:{ROBOT_PORT}...")
        pepper_controller = PepperController(robot_ip, ROBOT_PORT)
        logger.info("✓ Successfully connected to Pepper")
        
        # 2. Start the video streamer in a background thread
        logger.info("Starting video streaming service...")
        video_thread = threading.Thread(
            target=start_video_stream, 
            args=(robot_ip, ROBOT_PORT),
            daemon=True,
            name="VideoStreamThread"
        )
        video_thread.start()
        logger.info(f"✓ Video streaming thread started")
        
        # Give video thread time to initialize
        await asyncio.sleep(1)
        
        # 3. Start health monitoring
        health_task = asyncio.create_task(health_check_loop(pepper_controller))
        
        # 4. Start the WebSocket server for commands
        command_server = CommandReceiver(pepper_controller, '0.0.0.0', COMMAND_PORT)
        logger.info(f"✓ Starting command server on WebSocket port {COMMAND_PORT}...")
        logger.info("")
        logger.info("╔════════════════════════════════════════════════════════╗")
        logger.info("║              🚀 SERVER READY FOR VR                    ║")
        logger.info("╚════════════════════════════════════════════════════════╝")
        logger.info(f"WebSocket: ws://0.0.0.0:{COMMAND_PORT}")
        logger.info(f"Video Feed: http://0.0.0.0:{VIDEO_PORT}/video_feed")
        logger.info("")
        logger.info("Waiting for Unity client connection...")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("")
        
        # Start WebSocket server (blocks here)
        await command_server.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except ConnectionError as e:
        logger.error(f"❌ CONNECTION FAILED: {e}")
        logger.error("Please check:")
        logger.error("  1. Pepper's IP address is correct")
        logger.error("  2. Pepper is powered on and ready")
        logger.error("  3. Both devices are on the same network")
        logger.error("  4. Port 9559 is accessible: nc -zv {robot_ip} 9559")
    except Exception as e:
        logger.error(f"❌ FATAL ERROR during startup: {e}", exc_info=True)
        logger.error("Please check Pepper's IP address, network connection, and ensure NAOqi is running.")
    finally:
        # Cleanup
        if pepper_controller:
            logger.info("Shutting down robot controller...")
            pepper_controller.emergency_stop()
            pepper_controller.close()
        
        if health_task:
            health_task.cancel()

def validate_ip(ip_string):
    """Validate IP address format"""
    parts = ip_string.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False

def print_network_info():
    """Print helpful network information"""
    import socket
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        logger.info(f"Your PC's hostname: {hostname}")
        logger.info(f"Your PC's IP: {local_ip}")
        logger.info(f"Use this IP in Unity's PepperConnection.serverIp: \"{local_ip}\"")
        logger.info("")
    except Exception as e:
        logger.warning(f"Could not determine local IP: {e}")

if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Run the Pepper VR Teleoperation Server (qi framework)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --ip 192.168.1.100
  python main.py --ip 10.0.0.50 --verbose
  
Network Setup:
  1. Press Pepper's chest button to hear its IP address
  2. Ensure your laptop is on the same WiFi network as Pepper
  3. Test connection: ping <PEPPER_IP>
  4. Run this script with Pepper's IP
  5. Configure Unity with YOUR PC's IP (shown at startup)
        """
    )
    
    parser.add_argument(
        '--ip', 
        type=str, 
        default=DEFAULT_ROBOT_IP, 
        help=f"Pepper robot's IP address (default: {DEFAULT_ROBOT_IP})"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose debug logging"
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help="Only test connection and exit (don't start servers)"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate IP address
    if not validate_ip(args.ip):
        logger.error(f"❌ Invalid IP address format: {args.ip}")
        logger.error("Expected format: XXX.XXX.XXX.XXX (e.g., 192.168.1.100)")
        sys.exit(1)
    
    # Print network info
    print_network_info()
    
    # Test connection mode
    if args.test_connection:
        logger.info("Testing connection only (--test-connection mode)")
        try:
            import qi
            logger.info(f"Connecting to {args.ip}:{ROBOT_PORT}...")
            session = qi.Session()
            session.connect(f"tcp://{args.ip}:{ROBOT_PORT}")
            logger.info("✓ Connection successful!")
            
            motion = session.service("ALMotion")
            logger.info("✓ ALMotion service accessible")
            
            session.close()
            logger.info("\n🎉 Connection test passed! Ready to start full server.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            sys.exit(1)
    
    # Start the main server
    try:
        asyncio.run(main(args.ip))
    except KeyboardInterrupt:
        logger.info("\nServer shutting down...")
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)