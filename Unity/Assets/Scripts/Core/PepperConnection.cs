using UnityEngine;
using NativeWebSocket;
using System.Collections.Generic;

/// <summary>
/// Manages the WebSocket connection to the Python server.
/// FIXED: Command queue clearing on disconnect, better thread safety
/// </summary>
public class PepperConnection : MonoBehaviour
{
    // --- Singleton Pattern ---
    public static PepperConnection Instance { get; private set; }

    [Header("Network Settings")]
    public string serverIp = "192.168.1.129"; // IMPORTANT: Change this to your PC's IP
    public int serverPort = 5000;

    [Header("Connection Status")]
    [SerializeField]
    private bool isConnected = false;

    private WebSocket websocket;
    private Queue<object> commandQueue = new Queue<object>();
    private object queueLock = new object(); // FIXED: Added lock for thread safety

    void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
        }
        else
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }

    async void Start()
    {
        await Connect();
    }

    void Update()
    {
        #if !UNITY_WEBGL || UNITY_EDITOR
        if (websocket != null)
        {
            websocket.DispatchMessageQueue();
        }
        #endif

        // FIXED: Thread-safe queue processing
        if (isConnected)
        {
            lock (queueLock)
            {
                while (commandQueue.Count > 0)
                {
                    var command = commandQueue.Dequeue();
                    SendCommandInternal(command);
                }
            }
        }
    }

    private async void OnApplicationQuit()
    {
        if (websocket != null)
        {
            await websocket.Close();
        }
    }

    public void SendCommand(object command)
    {
        if (isConnected)
        {
            SendCommandInternal(command);
        }
        else
        {
            // FIXED: Thread-safe queue access
            lock (queueLock)
            {
                commandQueue.Enqueue(command);
            }
            Debug.LogWarning("Connection is closed. Queuing command.");
        }
    }

    public bool IsConnected()
    {
        return isConnected;
    }

    private async System.Threading.Tasks.Task Connect()
    {
        string serverUrl = $"ws://{serverIp}:{serverPort}";
        websocket = new WebSocket(serverUrl);

        websocket.OnOpen += () =>
        {
            Debug.Log("<color=green>Connection to Python server opened successfully!</color>");
            isConnected = true;
        };

        websocket.OnError += (e) =>
        {
            Debug.LogError("<color=red>Connection Error:</color> " + e);
            isConnected = false;
            
            // FIXED: Clear queue on error
            lock (queueLock)
            {
                commandQueue.Clear();
            }
        };

        websocket.OnClose += (e) =>
        {
            Debug.Log("<color=orange>Connection closed.</color> Code: " + e);
            isConnected = false;
            
            // FIXED: Clear command queue on disconnect to prevent stale commands
            lock (queueLock)
            {
                commandQueue.Clear();
                Debug.Log("Command queue cleared on disconnect");
            }
        };

        websocket.OnMessage += (bytes) =>
        {
            var message = System.Text.Encoding.UTF8.GetString(bytes);
            Debug.Log("Message received from server: " + message);
        };
        
        Debug.Log($"Attempting to connect to {serverUrl}...");
        await websocket.Connect();
    }

    private async void SendCommandInternal(object command)
    {
        if (websocket != null && websocket.State == WebSocketState.Open)
        {
            try
            {
                string jsonCommand = JsonUtility.ToJson(command);
                await websocket.SendText(jsonCommand);
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to send command: {e.Message}");
            }
        }
    }
}