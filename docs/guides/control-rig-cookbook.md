---
description: "Control Rig cookbook — Python recipes for building rigs, adding controls, inspecting bone hierarchies, and transforms in Unreal Engine."
---

# Control Rig Cookbook

Common recipes and patterns for Control Rig setup with PyUnreal.

---

## Inspect an Existing Rig

Load a Control Rig and explore its hierarchy.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Mannequin')

# Print all bones.
print('Bones:')
for bone in rig.bones:
    print(f'  {bone.name} (parent: {bone.parent})')

# Print all controls.
print('Controls:')
for ctrl in rig.controls:
    print(f'  {ctrl.name} (parent: {ctrl.parent})')

# Print all nulls (spaces/groups).
print('Nulls:')
for null in rig.nulls:
    print(f'  {null.name} (parent: {null.parent})')
```

---

## Add Controls to a Rig

Build a simple FK control chain.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Mannequin')

# Create a root null as a grouping element.
root = rig.add_null('Global', parent=None)

# Add body controls with colored shapes.
hips   = rig.add_control('Hips',     parent='Global', shape='Box',    color='yellow')
spine1 = rig.add_control('Spine_01', parent='Hips',   shape='Circle', color='yellow')
spine2 = rig.add_control('Spine_02', parent='Spine_01', shape='Circle', color='yellow')
chest  = rig.add_control('Chest',    parent='Spine_02', shape='Circle', color='yellow')

# Head and neck.
neck = rig.add_control('Neck', parent='Chest', shape='Circle', color='cyan')
head = rig.add_control('Head', parent='Neck',  shape='Diamond', color='cyan')

print('Controls:', [c.name for c in rig.controls])
```

---

## Color Presets

Controls support named color presets for quick setup.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Character')

# Available color names:
#   red, green, blue, yellow, cyan, magenta, orange, purple, white
rig.add_control('IK_Hand_L', parent='Global', color='blue')
rig.add_control('IK_Hand_R', parent='Global', color='red')

# Or use explicit RGBA tuples (0-1 range).
rig.add_control('Custom', parent='Global', color=(0.5, 0.8, 0.2, 1.0))
```

---

## Set Control Transforms

Position controls to match bone locations.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Character')

# Get a control by name.
hips = rig.get_control('Hips')

# Set the initial transform.
hips.set_transform(
    location=(0, 0, 100),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
)

# Read back the transform.
t = hips.transform
print('Location:', t['location'])
print('Rotation:', t['rotation'])
```

---

## Control Shapes

Customize control visual appearance.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Character')
ctrl = rig.get_control('Hips')

# Change the shape and color.
ctrl.set_shape(shape_name='Box', color='orange')
```

---

## Build a Full Arm Chain

Create an FK/IK arm setup from scratch.

```python
from pyunreal.control_rig import ControlRig

rig = ControlRig.load('/Game/Rigs/CR_Character')

# Left arm FK chain.
arm_grp = rig.add_null('Arm_L_Group', parent='Chest')

shoulder = rig.add_control('FK_Shoulder_L', parent='Arm_L_Group',
                           shape='Circle', color='blue')
elbow    = rig.add_control('FK_Elbow_L', parent='FK_Shoulder_L',
                           shape='Circle', color='blue')
wrist    = rig.add_control('FK_Wrist_L', parent='FK_Elbow_L',
                           shape='Circle', color='blue')

# IK target.
ik_hand = rig.add_control('IK_Hand_L', parent='Arm_L_Group',
                          shape='Box', color='green')
ik_pole = rig.add_control('IK_Pole_L', parent='Arm_L_Group',
                          shape='Diamond', color='green')

print('Arm controls created.')
```

---

## Search for Rigs

Use `find()` to search the asset registry for Control Rigs.

```python
from pyunreal.control_rig import ControlRig

# Find all Control Rigs matching a pattern.
rigs = ControlRig.find('CR_*')
for rig in rigs:
    print(rig.name, '-', len(rig.controls), 'controls,', len(rig.bones), 'bones')
```
