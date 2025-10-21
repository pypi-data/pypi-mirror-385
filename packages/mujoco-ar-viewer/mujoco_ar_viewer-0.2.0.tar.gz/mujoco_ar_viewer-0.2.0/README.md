# MuJoCo AR Viewer

A Python package for visualizing MuJoCo physics simulations in Augmented Reality using Apple Vision Pro and other AR devices.

![assets/diagram-mjar3.png](assets/diagram-mjar3.png)


## Installation

### Python API 

```bash
pip install mujoco-ar-viewer
```

To use automatic MuJoCo XML-to-USD conversion feature (supported only on Linux and Windows via [mujoco-usd-converter](https://github.com/newton-physics/mujoco-usd-converter) from project [Newton](https://github.com/newton-physics)), use: 

```bash 
pip install "mujoco-ar-viewer[usd]"
```




### VisionOS App 

Open App Store on VisionOS, and search for [mujocoARViewer]. 

## Quick Start

```python
from mujoco_arviewer import MJARViewer
import mujoco

# path to mujoco XML 
xml_path = "path/to/your/model.xml"

# Set up your MuJoCo simulation
model = mujoco.MjModel.from_xml_path(xml_path)
data = mujoco.MjData(model)

# Initialize the AR viewer with your device's IP
# Device's IP will be presented when you launch the app 
viewer = MJARViewer(avp_ip="192.168.1.100", \
                    enable_hand_tracking = True)
# Send a MuJoCo model to the AR device
# (Linux Only) it will automatically convert to USD
viewer.load_scene(xml_path) 
# Register the model and data with the viewer
viewer.register(model, data)

# Simulation loop
while True:
    # (Optional) access hand tracking results 
    hand_tracking = viewer.get_hand_tracking() 
    # (Optional) map hand tracking to mujoco ctrl
    data.ctrl = hand2ctrl(hand_tracking)

    # Step the simulation
    mujoco.mj_step(model, data)
    # Sync with AR device
    viewer.sync()
```

## Where to attach your mujoco `world` frame 


Since this is a viewer in augmented reality (which by defintion, blends your simulated environment with your real world environment), deciding where to attach your simulation scene's `world` frame in your actual physical space in real world is important. You can determine this by passing in `attach_to` as an argument either by 
1. a 7-dim vector of `xyz` translation and scalar-first quaternion representation (i.e., `[x,y,z,qw,qx,qy,qz]`)
2. a 4-dim vector of `xyz` translation and rotation around `z-axis`, specified as a degree. (i.e., `[x,y,z,zrot]`)

```python 
# attach the `world` frame 0.3m above the visionOS origin, rotating 90 degrees around z-axis. 
viewer.load_scene(scene_path, attach_to=[0, 0, 0.3, 90]) 
```

1. **Default Setting**: When `viewer.load_scene` is called without `attach_to` specified, it attahces the simualtion scene to the origin frame registered inside VisionOS. VisionOS automatically detects the physical ground of your surrounding using its sensors and defines the origin on the ground. For instance, if you're standing, visionOS will attach origin frame right below your feet. If you're sitting down, it's gonna be right below your chair. Below are scenarios when this default setting might be just right for you. We assume most of the mujoco XML files are using `Z-UP` convention. 
    - **Humanoid/Quadruped Locomotion Scenes**: Most of the humanoid/quadruped locomotion simulation environments have world frame attached to a surface actually defined as a "pyhsical ground". Then you don't need no offset, at least for the `z-axis`. Based on your use cases, you might still want to some offset for `x` and `y` translation, or rotation around `z-axis`. 

2. **(Possibly) Desirable Setting**: 

    - **Table-top Manipulation Scenes without explicit table modeling** : when your XML file is for table-top manipulation using fixed-base manipulators, and your 


2. 

## USD Conversion 


## Alternatives 



## Hand-Tracking Info 

Conventions 


## License

MIT License

