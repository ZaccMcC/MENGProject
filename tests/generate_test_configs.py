import json
import os
import copy

# Load full base config (make sure it includes aperture areas!)
with open("C:/Users/temp/IdeaProjects/MENGProject/config.json", "r") as f:
    base_config = json.load(f)

# Where to save generated test configs
output_dir = "C:/Users/temp/IdeaProjects/MENGProject/test_configs"
os.makedirs(output_dir, exist_ok=True)

def generate_test_config(test_name, sensor_positions, aperture_enabled, source_position, source_direction, num_lines, movement_type=None):
    config = copy.deepcopy(base_config)

    print(f"Movement type: {movement_type}")
    # Update source plane
    config["planes"]["source_plane"]["position"] = source_position
    config["planes"]["source_plane"]["direction"] = source_direction

    # Clear and repopulate sensor areas
    config["sensor_areas"] = {}
    for i, pos in enumerate(sensor_positions):
        config["sensor_areas"][f"sensor_{chr(65+i)}"] = {
            "title": f"A{i}",
            "position": pos,  # ✅ Must be [x, y, z]
            "direction": [0, 0, 1],
            "width": 1.5,
            "length": 1.5
        }

    config["output"]["Sim_title"] = test_name

    # Copy aperture areas if enabled
    if aperture_enabled:
        config["aperture_areas"] = copy.deepcopy(base_config["aperture_areas"])
    else:
        # Create one large aperture the size of the sensor plane
        config["aperture_areas"] = {
            "Full_Aperture": {
                "title": "Full_Aperture",
                "position": base_config["planes"]["aperture_plane"]["position"],
                "direction": base_config["planes"]["aperture_plane"]["direction"],
                "width": base_config["planes"]["sensor_plane"]["width"],
                "length": base_config["planes"]["sensor_plane"]["length"]
            }
        }

    # Simulation settings
    config["simulation"]["num_lines"] = num_lines
    config["simulation"]["num_runs"] = 1

    # Disable all movement styles unless specified
    config["arc_movement"]["horizontal_circles"] = False
    config["arc_movement"]["vertical_circles"] = False
    config["arc_movement"]["rigid_arc"] = False
    if movement_type == "rigid_arc" or movement_type is None:
        config["arc_movement"]["rigid_arc"] = True

    # Save the new config
    filename = f"{test_name}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)

    return filepath

# === Define Tests ===
test_configs = []

# Test 1: Sensor directly below source
test_configs.append(generate_test_config(
    "test_directly_below",
    [[0, 0, 0]],
    aperture_enabled=False,
    source_position=[0, 0, 1],
    source_direction=[0, 0, -1],
    num_lines=1000,
    movement_type = "rigid_arc"
))

# Test 2: Off-center sensors
test_configs.append(generate_test_config(
    "test_off_center",
    [[0, 0, 0], [2, 0, 0], [-2, 0, 0]],
    aperture_enabled=False,
    source_position=[0, 0, 1],
    source_direction=[0, 0, -1],
    num_lines=1000,
))

# Test 3: No intersections (pointing sideways)
test_configs.append(generate_test_config(
    "test_no_intersection",
    [[10, 10, 0]],
    aperture_enabled=False,
    source_position=[0, 0, 1],
    source_direction=[1, 0, 0],
    num_lines=500
))

# Test 4: With aperture active
test_configs.append(generate_test_config(
    "test_with_aperture",
    [[0, -2.25, 0]],
    aperture_enabled=True,
    source_position=[0, 0, 1],
    source_direction=[0, 0, -1],
    num_lines=1000
))

# Test 5: Arc movement
test_configs.append(generate_test_config(
    "test_arc_rotation",
    [[0, -3.25, 0], [0, -1.25, 0], [-1, 2.25, 0], [1, 2.25, 0]],
    aperture_enabled=True,
    source_position=[0, 0, 1],
    source_direction=[0, 0, -1],
    num_lines=1000,
    movement_type="rigid_arc"
))

print(f"✅ {len(test_configs)} test configs generated in:\n{output_dir}")
