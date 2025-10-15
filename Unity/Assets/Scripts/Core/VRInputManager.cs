using UnityEngine;
using UnityEngine.XR;

/// <summary>
/// Central VR input manager for Meta Quest 2. Polls all inputs and distributes them.
/// This version is updated for the "engage and release" arm control scheme.
/// </summary>
public class VRInputManager : MonoBehaviour
{
    [Header("XR References")]
    public XRNode leftHandNode = XRNode.LeftHand;
    public XRNode rightHandNode = XRNode.RightHand;
    public XRNode headNode = XRNode.Head;
    
    [Header("Input Devices")]
    private InputDevice leftController;
    private InputDevice rightController;
    private InputDevice headset;
    
    [Header("Controller States")]
    public Vector2 leftJoystick;
    public Vector2 rightJoystick;
    public float leftTrigger;
    public float rightTrigger;
    public bool leftGripPressed;
    public bool rightGripPressed;
    public bool buttonAPressed; // For HUD clicks (right controller)
    public bool buttonXPressed; // For HUD clicks (left controller)
    
    [Header("Poses")]
    public Vector3 leftHandPosition;
    public Quaternion leftHandRotation;
    public Vector3 rightHandPosition;
    public Quaternion rightHandRotation;
    public Quaternion headRotation;
    
    [Header("Settings")]
    [Range(0f, 0.3f)]
    public float joystickDeadzone = 0.1f;
    
    [Header("References to Controllers")]
    public BaseMovementController baseController;
    public ArmIKController armIKController;
    public HandController handController;
    public HeadController headController;
    // public HUDInteraction hudInteraction; // Link this if you create a HUD script

    private bool devicesInitialized = false;

    void Start()
    {
        InitializeDevices();
    }

    void Update()
    {
        if (!devicesInitialized)
        {
            InitializeDevices();
            return;
        }
        
        UpdateInputStates();
        UpdatePoses();
        DistributeInputs();
    }

    void InitializeDevices()
    {
        leftController = InputDevices.GetDeviceAtXRNode(leftHandNode);
        rightController = InputDevices.GetDeviceAtXRNode(rightHandNode);
        headset = InputDevices.GetDeviceAtXRNode(headNode);
        devicesInitialized = leftController.isValid && rightController.isValid && headset.isValid;
        if (devicesInitialized) Debug.Log("VR devices initialized successfully");
    }

    void UpdateInputStates()
    {
        leftController.TryGetFeatureValue(CommonUsages.primary2DAxis, out leftJoystick);
        leftController.TryGetFeatureValue(CommonUsages.trigger, out leftTrigger);
        leftController.TryGetFeatureValue(CommonUsages.gripButton, out leftGripPressed);
        leftController.TryGetFeatureValue(CommonUsages.primaryButton, out buttonXPressed);
        
        rightController.TryGetFeatureValue(CommonUsages.primary2DAxis, out rightJoystick);
        rightController.TryGetFeatureValue(CommonUsages.trigger, out rightTrigger);
        rightController.TryGetFeatureValue(CommonUsages.gripButton, out rightGripPressed);
        rightController.TryGetFeatureValue(CommonUsages.primaryButton, out buttonAPressed);
        
        leftJoystick = ApplyDeadzone(leftJoystick);
        rightJoystick = ApplyDeadzone(rightJoystick);
    }

    void UpdatePoses()
    {
        leftController.TryGetFeatureValue(CommonUsages.devicePosition, out leftHandPosition);
        leftController.TryGetFeatureValue(CommonUsages.deviceRotation, out leftHandRotation);
        rightController.TryGetFeatureValue(CommonUsages.devicePosition, out rightHandPosition);
        rightController.TryGetFeatureValue(CommonUsages.deviceRotation, out rightHandRotation);
        headset.TryGetFeatureValue(CommonUsages.deviceRotation, out headRotation);
    }

    void DistributeInputs()
    {
        if (baseController != null) baseController.UpdateMovement(leftJoystick, rightJoystick.x);
        if (handController != null) handController.UpdateHandStates(leftTrigger, rightTrigger);
        if (headController != null) headController.UpdateHeadTarget(headRotation);
        
        if (armIKController != null)
        {
            armIKController.UpdateArmControl(
                leftGripPressed, rightGripPressed,
                leftHandPosition, leftHandRotation,
                rightHandPosition, rightHandRotation
            );
        }

        // if (hudInteraction != null)
        // {
        //     bool hudSelectPressed = buttonAPressed || buttonXPressed;
        //     hudInteraction.UpdateInteraction(hudSelectPressed);
        // }
    }

    Vector2 ApplyDeadzone(Vector2 input)
    {
        if (input.magnitude < joystickDeadzone) return Vector2.zero;
        return input.normalized * ((input.magnitude - joystickDeadzone) / (1f - joystickDeadzone));
    }
}