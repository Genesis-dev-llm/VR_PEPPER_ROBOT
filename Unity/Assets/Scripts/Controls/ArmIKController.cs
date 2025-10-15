using UnityEngine;

public class ArmIKController : MonoBehaviour
{
    private enum ArmState { Idle, Mimicking }

    [Header("Network Reference")]
    public PepperConnection pepperConnection;
    
    [Header("IK Solvers")]
    public IKSolver leftArmSolver;
    public IKSolver rightArmSolver;

    [Header("Arm Settings")]
    [Range(0f, 1f)] public float movementSpeed = 0.3f;
    [Range(0f, 1f)] public float smoothingFactor = 0.15f;

    [Header("Coordinate Transformation")]
    public Transform vrOrigin;
    public Vector3 scaleVRToPepper = Vector3.one;
    public Vector3 offsetVRToPepper = Vector3.zero;

    private ArmState leftArmState = ArmState.Idle;
    private ArmState rightArmState = ArmState.Idle;

    private PepperArmJoints leftArmCurrent;
    private PepperArmJoints rightArmCurrent;
    private PepperArmJoints leftArmTarget;
    private PepperArmJoints rightArmTarget;

    void Start()
    {
        if (pepperConnection == null) pepperConnection = PepperConnection.Instance;
        if (vrOrigin == null) vrOrigin = FindObjectOfType<VRInputManager>()?.transform;
        
        leftArmCurrent = PepperArmJoints.DefaultPose();
        rightArmCurrent = PepperArmJoints.DefaultPose();
        leftArmTarget = PepperArmJoints.DefaultPose();
        rightArmTarget = PepperArmJoints.DefaultPose();
    }

    public void UpdateArmControl(bool isLeftGripPressed, bool isRightGripPressed, 
                                 Vector3 leftPos, Quaternion leftRot, 
                                 Vector3 rightPos, Quaternion rightRot)
    {
        if (isLeftGripPressed && leftArmState == ArmState.Idle) leftArmState = ArmState.Mimicking;
        else if (!isLeftGripPressed && leftArmState == ArmState.Mimicking) leftArmState = ArmState.Idle;

        if (isRightGripPressed && rightArmState == ArmState.Idle) rightArmState = ArmState.Mimicking;
        else if (!isRightGripPressed && rightArmState == ArmState.Mimicking) rightArmState = ArmState.Idle;
        
        bool shouldSendCommands = false;
        if (leftArmState == ArmState.Mimicking && leftArmSolver != null)
        {
            UpdateArmTarget(ref leftArmTarget, leftArmSolver, leftPos, leftRot, "left");
            shouldSendCommands = true;
        }
        
        if (rightArmState == ArmState.Mimicking && rightArmSolver != null)
        {
            UpdateArmTarget(ref rightArmTarget, rightArmSolver, rightPos, rightRot, "right");
            shouldSendCommands = true;
        }

        if (shouldSendCommands)
        {
            leftArmCurrent = PepperArmJoints.Lerp(leftArmCurrent, leftArmTarget, smoothingFactor);
            rightArmCurrent = PepperArmJoints.Lerp(rightArmCurrent, rightArmTarget, smoothingFactor);
            SendArmCommands();
        }
    }

    private void UpdateArmTarget(ref PepperArmJoints armTarget, IKSolver solver, Vector3 controllerPos, Quaternion controllerRot, string side)
    {
        Vector3 targetPos = TransformVRToPepper(controllerPos);
        Vector3[] chain = solver.Solve(targetPos);
        if (chain != null)
        {
            armTarget = CalculateJointAngles(chain, controllerRot, side, solver.shoulderOrigin);
        }
    }
    
    private PepperArmJoints CalculateJointAngles(Vector3[] chain, Quaternion handRotation, string side, Transform shoulderOrigin)
    {
        PepperArmJoints newJoints = new PepperArmJoints();

        Vector3 shoulderPos = chain[0], elbowPos = chain[1], wristPos = chain[2];
        Vector3 shoulderToElbow = (elbowPos - shoulderPos).normalized;
        Vector3 elbowToWrist = (wristPos - elbowPos).normalized;

        Vector3 shoulderFwd = shoulderOrigin.forward, shoulderUp = shoulderOrigin.up, shoulderRight = shoulderOrigin.right;

        float elbowAngle = Vector3.Angle(shoulderToElbow, -elbowToWrist);
        newJoints.elbowRoll = -elbowAngle * Mathf.Deg2Rad;

        Vector3 pitchVector = Vector3.ProjectOnPlane(shoulderToElbow, shoulderRight);
        newJoints.shoulderPitch = Vector3.SignedAngle(shoulderFwd, pitchVector, shoulderRight) * Mathf.Deg2Rad;

        Vector3 rollVector = Vector3.ProjectOnPlane(shoulderToElbow, shoulderFwd);
        float rollAngle = Vector3.SignedAngle(shoulderUp, rollVector, shoulderFwd); 
        newJoints.shoulderRoll = rollAngle * Mathf.Deg2Rad;
        
        Vector3 handUp = handRotation * Vector3.up;
        Vector3 handFwd = handRotation * Vector3.forward;

        Vector3 planeNormal = elbowToWrist;
        Vector3 projectedHandUp = Vector3.ProjectOnPlane(handUp, planeNormal);
        Vector3 referenceVector = Vector3.ProjectOnPlane(shoulderUp, planeNormal);
        newJoints.wristYaw = Vector3.SignedAngle(referenceVector, projectedHandUp, planeNormal) * Mathf.Deg2Rad;

        Vector3 armPlaneNormal = Vector3.Cross(shoulderToElbow, elbowToWrist);
        Vector3 projectedHandFwd = Vector3.ProjectOnPlane(handFwd, armPlaneNormal);
        newJoints.elbowYaw = Vector3.SignedAngle(elbowToWrist, projectedHandFwd, armPlaneNormal) * Mathf.Deg2Rad;

        if (side == "left")
        {
            newJoints.shoulderRoll *= -1;
            newJoints.elbowYaw *= -1;
            newJoints.wristYaw *= -1;
        }

        return newJoints;
    }

    Vector3 TransformVRToPepper(Vector3 vrPosition)
    {
        Vector3 worldPos = vrOrigin.TransformPoint(vrPosition);
        return Vector3.Scale(worldPos, scaleVRToPepper) + offsetVRToPepper;
    }

    void SendArmCommands()
    {
        if (pepperConnection == null || !pepperConnection.IsConnected()) return;

        if (leftArmState == ArmState.Mimicking)
        {
            var leftCmd = new ArmCommand { type = "arm_move", side = "left", joints = leftArmCurrent, speed = movementSpeed };
            pepperConnection.SendCommand(leftCmd);
        }
        if (rightArmState == ArmState.Mimicking)
        {
            var rightCmd = new ArmCommand { type = "arm_move", side = "right", joints = rightArmCurrent, speed = movementSpeed };
            pepperConnection.SendCommand(rightCmd);
        }
    }
}

[System.Serializable]
public class PepperArmJoints
{
    public float shoulderPitch, shoulderRoll, elbowYaw, elbowRoll, wristYaw;
    public static PepperArmJoints DefaultPose() { return new PepperArmJoints { shoulderPitch = 0, shoulderRoll = 0, elbowYaw = 0, elbowRoll = 0, wristYaw = 0 }; }
    public static PepperArmJoints Lerp(PepperArmJoints a, PepperArmJoints b, float t)
    {
        return new PepperArmJoints
        {
            shoulderPitch = Mathf.Lerp(a.shoulderPitch, b.shoulderPitch, t),
            shoulderRoll = Mathf.Lerp(a.shoulderRoll, b.shoulderRoll, t),
            elbowYaw = Mathf.Lerp(a.elbowYaw, b.elbowYaw, t),
            elbowRoll = Mathf.Lerp(a.elbowRoll, b.elbowRoll, t),
            wristYaw = Mathf.Lerp(a.wristYaw, b.wristYaw, t)
        };
    }
}

[System.Serializable]
public class ArmCommand
{
    public string type;
    public string side;
    public PepperArmJoints joints;
    public float speed;
}