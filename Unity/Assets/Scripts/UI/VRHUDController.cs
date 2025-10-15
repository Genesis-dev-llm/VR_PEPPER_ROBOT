using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

/// <summary>
/// VR HUD Controller for Pepper teleoperation
/// Displays status, video feed, and control buttons
/// </summary>
public class VRHUDController : MonoBehaviour
{
    [Header("References")]
    public PepperConnection pepperConnection;
    public VideoFeedDisplay videoFeed;
    public Transform vrCamera;
    
    [Header("HUD Panels")]
    public GameObject statusPanel;
    public GameObject videoPanel;
    public GameObject controlPanel;
    
    [Header("Status UI Elements")]
    public Text connectionStatusText;
    public Text batteryText;
    public Text modeText;
    public Image connectionIndicator;
    
    [Header("Video Display")]
    public RawImage videoDisplay;
    
    [Header("Control Buttons")]
    public Button waveButton;
    public Button danceButton;
    public Button standButton;
    public Button restButton;
    public Button emergencyStopButton;
    
    [Header("HUD Positioning")]
    [Tooltip("Distance from camera")]
    public float hudDistance = 2.0f;
    
    [Tooltip("Height offset from camera")]
    public float hudHeightOffset = -0.3f;
    
    [Tooltip("Follow camera smoothly")]
    public bool followCamera = true;
    
    [Range(0f, 1f)]
    public float followSmoothing = 0.1f;
    
    [Header("Interaction")]
    public bool hudVisible = true;
    public KeyCode toggleKey = KeyCode.H;  // For testing in editor
    
    private string currentMode = "IDLE";
    private Color connectedColor = new Color(0f, 1f, 0f, 1f);
    private Color disconnectedColor = new Color(1f, 0f, 0f, 1f);

    void Start()
    {
        // Find references if not assigned
        if (pepperConnection == null)
            pepperConnection = PepperConnection.Instance;
        
        if (videoFeed == null)
            videoFeed = FindObjectOfType<VideoFeedDisplay>();
        
        if (vrCamera == null)
            vrCamera = Camera.main?.transform;
        
        // Setup button listeners
        SetupButtons();
        
        // Link video feed to HUD
        if (videoFeed != null && videoDisplay != null)
        {
            videoFeed.targetRawImage = videoDisplay;
        }
        
        // Initial positioning
        PositionHUD();
        
        Debug.Log("VR HUD initialized");
    }

    void SetupButtons()
    {
        if (waveButton != null)
            waveButton.onClick.AddListener(() => SendPreMotion("wave"));
        
        if (danceButton != null)
            danceButton.onClick.AddListener(() => SendPreMotion("dance"));
        
        if (standButton != null)
            standButton.onClick.AddListener(() => SendPreMotion("stand"));
        
        if (restButton != null)
            restButton.onClick.AddListener(() => SendPreMotion("rest"));
        
        if (emergencyStopButton != null)
        {
            emergencyStopButton.onClick.AddListener(EmergencyStop);
            // Make emergency button visually distinct
            ColorBlock colors = emergencyStopButton.colors;
            colors.normalColor = Color.red;
            colors.highlightedColor = new Color(1f, 0.3f, 0.3f);
            emergencyStopButton.colors = colors;
        }
    }

    void Update()
    {
        // Update status displays
        UpdateStatusDisplay();
        
        // Handle HUD positioning
        if (followCamera && vrCamera != null)
        {
            PositionHUD();
        }
        
        // Toggle visibility (for testing)
        if (Input.GetKeyDown(toggleKey))
        {
            ToggleHUD();
        }
    }

    void PositionHUD()
    {
        if (vrCamera == null) return;
        
        // Calculate target position
        Vector3 targetPosition = vrCamera.position + 
                                 vrCamera.forward * hudDistance + 
                                 Vector3.up * hudHeightOffset;
        
        // Calculate target rotation (face the camera)
        Quaternion targetRotation = Quaternion.LookRotation(
            transform.position - vrCamera.position
        );
        
        if (followSmoothing > 0f)
        {
            // Smooth follow
            transform.position = Vector3.Lerp(
                transform.position, 
                targetPosition, 
                followSmoothing
            );
            transform.rotation = Quaternion.Slerp(
                transform.rotation, 
                targetRotation, 
                followSmoothing
            );
        }
        else
        {
            // Instant follow
            transform.position = targetPosition;
            transform.rotation = targetRotation;
        }
    }

    void UpdateStatusDisplay()
    {
        if (pepperConnection == null) return;
        
        // Connection status
        bool isConnected = pepperConnection.IsConnected();
        
        if (connectionStatusText != null)
        {
            connectionStatusText.text = isConnected ? "CONNECTED" : "DISCONNECTED";
            connectionStatusText.color = isConnected ? connectedColor : disconnectedColor;
        }
        
        if (connectionIndicator != null)
        {
            connectionIndicator.color = isConnected ? connectedColor : disconnectedColor;
        }
        
        // Mode display
        if (modeText != null)
        {
            modeText.text = $"MODE: {currentMode}";
        }
        
        // Battery (would need to implement status query from Python)
        if (batteryText != null)
        {
            batteryText.text = "BATTERY: ---%";  // Placeholder
        }
    }

    void SendPreMotion(string motionName)
    {
        if (pepperConnection == null || !pepperConnection.IsConnected())
        {
            Debug.LogWarning("Cannot send pre-motion: not connected");
            return;
        }
        
        var command = new PreMotionCommand
        {
            type = "pre_motion",
            motion_name = motionName
        };
        
        pepperConnection.SendCommand(command);
        currentMode = $"PLAYING: {motionName.ToUpper()}";
        
        Debug.Log($"Triggered pre-motion: {motionName}");
        
        // Reset mode after animation duration (rough estimate)
        Invoke(nameof(ResetMode), 5f);
    }

    void EmergencyStop()
    {
        if (pepperConnection == null) return;
        
        var command = new EmergencyStopCommand
        {
            type = "emergency_stop"
        };
        
        pepperConnection.SendCommand(command);
        currentMode = "EMERGENCY STOP";
        
        Debug.LogWarning("EMERGENCY STOP TRIGGERED");
        
        // Flash the emergency button
        StartCoroutine(FlashEmergencyButton());
    }

    System.Collections.IEnumerator FlashEmergencyButton()
    {
        if (emergencyStopButton == null) yield break;
        
        for (int i = 0; i < 3; i++)
        {
            emergencyStopButton.gameObject.SetActive(false);
            yield return new WaitForSeconds(0.2f);
            emergencyStopButton.gameObject.SetActive(true);
            yield return new WaitForSeconds(0.2f);
        }
    }

    void ResetMode()
    {
        currentMode = "IDLE";
    }

    public void ToggleHUD()
    {
        hudVisible = !hudVisible;
        gameObject.SetActive(hudVisible);
        Debug.Log($"HUD {(hudVisible ? "shown" : "hidden")}");
    }

    public void ShowPanel(string panelName)
    {
        switch (panelName.ToLower())
        {
            case "status":
                if (statusPanel) statusPanel.SetActive(true);
                break;
            case "video":
                if (videoPanel) videoPanel.SetActive(true);
                break;
            case "control":
                if (controlPanel) controlPanel.SetActive(true);
                break;
        }
    }

    public void HidePanel(string panelName)
    {
        switch (panelName.ToLower())
        {
            case "status":
                if (statusPanel) statusPanel.SetActive(false);
                break;
            case "video":
                if (videoPanel) videoPanel.SetActive(false);
                break;
            case "control":
                if (controlPanel) controlPanel.SetActive(false);
                break;
        }
    }

    public void SetMode(string mode)
    {
        currentMode = mode;
    }
}

// Command classes for HUD
[System.Serializable]
public class PreMotionCommand
{
    public string type;
    public string motion_name;
}

[System.Serializable]
public class EmergencyStopCommand
{
    public string type;
}