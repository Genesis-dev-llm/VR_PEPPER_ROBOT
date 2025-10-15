using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

/// <summary>
/// Displays Pepper's camera feed in VR as a texture
/// Fetches MJPEG stream from Python Flask server
/// </summary>
public class VideoFeedDisplay : MonoBehaviour
{
    [Header("Server Configuration")]
    [Tooltip("Python server IP address (same as PepperConnection.serverIp)")]
    public string serverIp = "192.168.1.101";
    
    [Tooltip("Video streaming port (should be 8080)")]
    public int videoPort = 8080;
    
    [Header("Display Settings")]
    [Tooltip("Material that will display the video (assign a Quad or UI RawImage)")]
    public Renderer targetRenderer;
    
    [Tooltip("Alternative: UI RawImage for HUD display")]
    public UnityEngine.UI.RawImage targetRawImage;
    
    [Header("Streaming Options")]
    [Tooltip("Automatically start streaming when script loads")]
    public bool autoStart = true;
    
    [Tooltip("Frame update interval in seconds (lower = higher framerate but more bandwidth)")]
    [Range(0.016f, 0.2f)]
    public float updateInterval = 0.033f;  // ~30 FPS
    
    [Header("Debug")]
    public bool showDebugInfo = true;
    
    private Texture2D videoTexture;
    private string streamUrl;
    private bool isStreaming = false;
    private float lastFrameTime = 0f;
    private int frameCount = 0;

    void Start()
    {
        streamUrl = $"http://{serverIp}:{videoPort}/video_feed";
        
        if (showDebugInfo)
        {
            Debug.Log($"Video Feed Display initialized. Stream URL: {streamUrl}");
        }
        
        // Validate we have a display target
        if (targetRenderer == null && targetRawImage == null)
        {
            Debug.LogError("VideoFeedDisplay: No display target assigned! Assign either targetRenderer or targetRawImage.");
            this.enabled = false;
            return;
        }
        
        if (autoStart)
        {
            StartStreaming();
        }
    }

    public void StartStreaming()
    {
        if (isStreaming)
        {
            Debug.LogWarning("Video stream already running");
            return;
        }
        
        isStreaming = true;
        StartCoroutine(StreamVideo());
        
        if (showDebugInfo)
        {
            Debug.Log("Started video streaming from Pepper");
        }
    }

    public void StopStreaming()
    {
        isStreaming = false;
        
        if (showDebugInfo)
        {
            Debug.Log("Stopped video streaming");
        }
    }

    IEnumerator StreamVideo()
    {
        // Create texture if needed
        if (videoTexture == null)
        {
            videoTexture = new Texture2D(640, 480, TextureFormat.RGB24, false);
            ApplyTextureToDisplay();
        }
        
        while (isStreaming)
        {
            // Use UnityWebRequestTexture for efficient image loading
            using (UnityWebRequest www = UnityWebRequestTexture.GetTexture(streamUrl))
            {
                // Set timeout
                www.timeout = 5;
                
                yield return www.SendWebRequest();
                
                if (www.result == UnityWebRequest.Result.Success)
                {
                    // Get the downloaded texture
                    Texture2D downloadedTexture = DownloadHandlerTexture.GetContent(www);
                    
                    if (downloadedTexture != null)
                    {
                        // Copy to our persistent texture
                        Graphics.CopyTexture(downloadedTexture, videoTexture);
                        
                        // Update frame counter
                        frameCount++;
                        lastFrameTime = Time.time;
                        
                        // Clean up temporary texture
                        Destroy(downloadedTexture);
                    }
                }
                else
                {
                    if (showDebugInfo)
                    {
                        Debug.LogWarning($"Video stream error: {www.error}");
                    }
                    
                    // Wait a bit before retrying on error
                    yield return new WaitForSeconds(1f);
                }
            }
            
            // Control frame rate
            yield return new WaitForSeconds(updateInterval);
        }
    }

    void ApplyTextureToDisplay()
    {
        if (targetRenderer != null)
        {
            targetRenderer.material.mainTexture = videoTexture;
            if (showDebugInfo)
            {
                Debug.Log("Video texture applied to Renderer");
            }
        }
        
        if (targetRawImage != null)
        {
            targetRawImage.texture = videoTexture;
            if (showDebugInfo)
            {
                Debug.Log("Video texture applied to RawImage");
            }
        }
    }

    void OnDestroy()
    {
        StopStreaming();
        
        if (videoTexture != null)
        {
            Destroy(videoTexture);
        }
    }

    void OnGUI()
    {
        if (!showDebugInfo) return;
        
        GUIStyle style = new GUIStyle();
        style.fontSize = 20;
        style.normal.textColor = Color.white;
        
        GUI.Label(new Rect(10, 10, 400, 30), 
            $"Video Stream: {(isStreaming ? "ACTIVE" : "STOPPED")}", style);
        GUI.Label(new Rect(10, 35, 400, 30), 
            $"Frames: {frameCount} | FPS: {GetCurrentFPS():F1}", style);
        GUI.Label(new Rect(10, 60, 400, 30), 
            $"Stream URL: {streamUrl}", style);
    }

    float GetCurrentFPS()
    {
        if (frameCount < 2) return 0f;
        float timeDiff = Time.time - lastFrameTime;
        if (timeDiff < 0.001f) return 0f;
        return 1f / updateInterval;
    }
    
    // Public API for external control
    public bool IsStreaming() => isStreaming;
    public Texture2D GetCurrentFrame() => videoTexture;
    public int GetFrameCount() => frameCount;
}