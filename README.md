# Pepper VR Teleoperation System

This project is a real-time, low-latency teleoperation system for a SoftBank Robotics Pepper robot, controlled via a Meta Quest 2 VR headset. The system allows for intuitive, one-to-one mimicry of the operator's head and arm movements.

## Features

-   **Full Upper-Body Mimicry:** Real-time control of Pepper's head, arms, and hands.
-   **VR-Based Locomotion:** Drive the robot's base using the VR controller joysticks.
-   **Inverse Kinematics (IK):** A custom FABRIK IK solver translates the operator's hand positions into valid joint angles for Pepper's 5-DOF arms.
-   **Engage/Release Control:** Arm mimicry is activated by holding the controller's grip button, providing a non-fatiguing and deliberate control scheme.
-   **Live Camera Feed:** See through the robot's eyes with a video stream displayed in the VR headset.

## Architecture

The system uses a client-server architecture over a local Wi-Fi network.

-   **Client (Unity):** A Unity application running on a Meta Quest 2 captures VR input, runs the IK solver, and sends JSON-based commands.
-   **Server (Python):** A modular Python server running on a local PC receives commands, translates them into NAOqi API calls, and streams the robot's camera feed back to the client.

## Setup and Installation

### 1. Python Server Setup

The `naoqi-python` SDK is required and must be installed manually.

1.  **Download the SDK:** Clone the official Aldebaran repository:
    ```bash
    git clone https://github.com/aldebaran/pynaoqi-python2.7-2.5.5.5-linux64.git
    ```
2.  **Set Environment Variable:** Before running the server, you must set the `PYTHONPATH` to point to the downloaded SDK.
    ```bash
    # Replace the path with the actual path on your machine
    export PYTHONPATH="/path/to/pynaoqi-python2.7-2.5.5.5-linux64/lib/python2.7/site-packages":$PYTHONPATH
    ```
3.  **Install Dependencies:** Navigate to the `Python/` directory and install the remaining packages.
    ```bash
    cd Python/
    pip install -r requirements.txt
    ```
4.  **Run the Server:**
    ```bash
    python main.py --ip <YOUR_PEPPER_IP>
    ```

### 2. Unity Client Setup

1.  Open the `Unity/` project in Unity Hub (Version 2022.3 LTS recommended).
2.  Install the required packages (`Meta XR SDK`, `NativeWebSocket`).
3.  Open the main scene and set the `Server Ip` field on the `_Managers` GameObject to the IP of the PC running the Python server.
4.  Build and run the project on a Meta Quest 2 headset in Developer Mode.