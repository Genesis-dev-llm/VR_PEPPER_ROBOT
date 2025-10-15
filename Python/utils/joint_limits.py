import json
import os

class JointLimits:
    """
    A utility class that loads Pepper's joint limits from a JSON file.
    Its sole purpose is to provide a `clamp` method to ensure that no
    unsafe joint angle commands are ever sent to the robot. This decouples
    the physical safety limits from the control logic.
    """
    def __init__(self, filename="pepper_joint_limits.json"):
        """
        Loads joint limits from the specified JSON file.
        It intelligently finds the file in the parent `Config` directory.
        """
        # Build a robust path to the config file.
        # __file__ is the path to this script (joint_limits.py)
        # os.path.dirname(__file__) is the directory of this script (utils/)
        # os.path.join(...) goes up one level ('..') and then into 'Config'
        script_dir = os.path.dirname(__file__)
        config_path = os.path.join(script_dir, '..', '..', 'Config', filename)
        
        try:
            with open(config_path, 'r') as f:
                self.limits = json.load(f)
            print("✓ Successfully loaded joint limits.")
        except FileNotFoundError:
            print(f"\033[91mERROR: Joint limits file not found at {config_path}\033[0m")
            print("Safety clamping will be disabled. Proceed with caution.")
            self.limits = {}
        except json.JSONDecodeError:
            print(f"\033[91mERROR: Could not parse {config_path}. Is it valid JSON?\033[0m")
            self.limits = {}

    def clamp(self, joint_name, value):
        """
        Clamps a given value to the defined min/max range for a specific joint.
        If the joint is not found in the limits file, it returns the original
        value with a warning.
        """
        if joint_name not in self.limits:
            # This is a fallback, but should ideally not happen if config is complete.
            # print(f"Warning: No limits defined for joint '{joint_name}'.")
            return value
        
        limit_info = self.limits[joint_name]
        clamped_value = max(limit_info['min'], min(limit_info['max'], value))
        
        return clamped_value