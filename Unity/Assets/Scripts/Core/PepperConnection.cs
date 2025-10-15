using UnityEngine;
using NativeWebSocket;
using System.Collections.Generic;

/// <summary>
/// Manages the WebSocket connection to the Python server.
/// Acts as a central hub for sending commands to Pepper.
/// Implemented as a Singleton to be easily accessible from any script.
/// </summary>
public class PepperConnection : MonoBehaviour
{
    // --- Singleton Pattern ---
    public static PepperConnection Instance { get; private set; }

    [Header("Network Settings")]
    public string serverIp = "192.168.1.101"; // IMPORTANT: Change this to your PC's IP
    public int serverPort = 5000;

    [Header("Connection Status")]
    [SerializeField]
    private bool isConnected = false;

    private WebSocket websocket;
    private Queue<object> commandQueue = new Queue<object>();

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

        if (isConnected && commandQueue.Count > 0)
        {
            while (commandQueue.Count > 0)
            {
                var command = commandQueue.Dequeue();
                SendCommandInternal(command);
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
            commandQueue.Enqueue(command);
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
        };

        websocket.OnClose += (e) =>
        {
            Debug.Log("<color=orange>Connection closed.</color> Code: " + e);
            isConnected = false;
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
        if (websocket.State == WebSocketState.Open)
        {
            string jsonCommand = JsonUtility.ToJson(command);
            await websocket.SendText(jsonCommand);
        }
    }
}