using UnityEngine;

public class HandController : MonoBehaviour
{
    [Header("Network Reference")]
    public PepperConnection pepperConnection;
    
    [Header("Hand Settings")]
    [Range(0f, 1f)] public float smoothingFactor = 0.1f;
    [Range(0f, 1f)] public float triggerThreshold = 0.05f;
    
    private float leftHandCurrent = 1f, rightHandCurrent = 1f;

    void Start()
    {
        if (pepperConnection == null)
        {
            pepperConnection = PepperConnection.Instance;
            if (pepperConnection == null)
            {
                Debug.LogError("PepperConnection instance not found!");
                this.enabled = false;
            }
        }
    }

    public void UpdateHandStates(float leftTrigger, float rightTrigger)
    {
        float leftHandTarget = 1f - Mathf.Clamp01(leftTrigger);
        float rightHandTarget = 1f - Mathf.Clamp01(rightTrigger);
        
        if (leftTrigger < triggerThreshold) leftHandTarget = 1f;
        if (rightTrigger < triggerThreshold) rightHandTarget = 1f;
        
        leftHandCurrent = Mathf.Lerp(leftHandCurrent, leftHandTarget, smoothingFactor);
        rightHandCurrent = Mathf.Lerp(rightHandCurrent, rightHandTarget, smoothingFactor);
        
        SendHandCommands();
    }

    void SendHandCommands()
    {
        if (pepperConnection == null || !pepperConnection.IsConnected()) return;
        
        var leftCmd = new HandCommand { type = "hand_move", side = "left", value = leftHandCurrent };
        var rightCmd = new HandCommand { type = "hand_move", side = "right", value = rightHandCurrent };
        
        pepperConnection.SendCommand(leftCmd);
        pepperConnection.SendCommand(rightCmd);
    }
}

[System.Serializable]
public class HandCommand
{
    public string type;
    public string side;
    public float value;
}