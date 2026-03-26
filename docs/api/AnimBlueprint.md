# AnimBlueprint

```python
from pyunreal.anim import AnimBlueprint
```

Pythonic wrapper around a `UAnimBlueprint` asset.  The entry point for all
AnimBP authoring -- create new AnimBPs, load existing ones, add state machines,
and compile.

**Requires:** MCA Editor plugin (for graph editing operations).

---

## Class Methods

### AnimBlueprint.create()

```python
AnimBlueprint.create(package_path, asset_name, skeleton)
```

Create a new Animation Blueprint in the Content Browser.

| Parameter | Type | Description |
|-----------|------|-------------|
| `package_path` | `str` | Content Browser folder (e.g. `'/Game/AnimBP'`) |
| `asset_name` | `str` | Name for the new asset |
| `skeleton` | `unreal.Skeleton` | Skeleton asset (from `load()`) |

**Returns:** `AnimBlueprint` instance.

**Raises:** `InvalidOperationError` if creation fails.

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

skeleton = load('/Game/Characters/Meshes/SK_Mannequin')
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Character', skeleton)
print(abp.name)  # 'ABP_Character'
```

---

### AnimBlueprint.load()

```python
AnimBlueprint.load(asset_path)
```

Load an existing Animation Blueprint from the Content Browser.

| Parameter | Type | Description |
|-----------|------|-------------|
| `asset_path` | `str` | Full content path to the AnimBP |

**Returns:** `AnimBlueprint` instance.

**Raises:**
- `AssetNotFoundError` if no asset at the path.
- `InvalidOperationError` if the asset is not an AnimBlueprint.

```python
abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')
print(abp.state_machines)  # [<StateMachine 'Locomotion'>]
```

---

## Properties

All properties are read-only.

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | The asset name |
| `path` | `str` | Full Content Browser path |
| `skeleton` | `unreal.Skeleton` | The target skeleton |
| `state_machines` | `list[StateMachine]` | All state machines (queries live state) |
| `ue_object` | `unreal.AnimBlueprint` | Direct access to the underlying UE object |

```python
abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')
print(abp.name)        # 'ABP_Character'
print(abp.path)        # '/Game/AnimBP/ABP_Character.ABP_Character'
print(abp.skeleton)    # <Skeleton 'SK_Mannequin'>

for sm in abp.state_machines:
    print(sm.name)     # 'Locomotion'
```

---

## Methods

### add_state_machine()

```python
abp.add_state_machine(name, connect_to_root=True)
```

Add a new state machine to the AnimGraph.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | | Name for the state machine |
| `connect_to_root` | `bool` | `True` | Wire output to the AnimGraph's final pose |

**Returns:** [`StateMachine`](StateMachine.md) instance.

**Raises:** `InvalidOperationError` if a state machine with this name already exists.

```python
# Primary locomotion state machine, wired to output
loco = abp.add_state_machine('Locomotion', connect_to_root=True)

# Secondary state machine, not wired (for layered blending)
upper_body = abp.add_state_machine('UpperBody', connect_to_root=False)
```

---

### compile()

```python
abp.compile()
```

Compile the AnimBlueprint.  Call this after setting up all states, transitions,
and animations.

**Returns:** `True` on success.

**Raises:** `InvalidOperationError` if compilation fails (check UE Output Log for details).

```python
# Always compile after making changes
result = abp.compile()
print("Compiled:", result)  # True
```

---

## Full Example

```python
from pyunreal import load
from pyunreal.anim import AnimBlueprint

# Create
skeleton = load('/Game/Characters/Meshes/SK_Mannequin')
abp = AnimBlueprint.create('/Game/AnimBP', 'ABP_Locomotion', skeleton)

# Build state machine
loco = abp.add_state_machine('Locomotion')

idle = loco.add_state('Idle', animation=load('/Game/Anims/Idle'), default=True)
walk = loco.add_state('Walk', animation=load('/Game/Anims/Walk'))
run  = loco.add_state('Run',  animation=load('/Game/Anims/Run'))

idle.transition_to(walk, crossfade=0.2)
walk.transition_to(idle, crossfade=0.2)
walk.transition_to(run,  crossfade=0.15)
run.transition_to(walk,  crossfade=0.15)

# Compile
abp.compile()

# Inspect
print(abp.name)                                    # 'ABP_Locomotion'
print([sm.name for sm in abp.state_machines])       # ['Locomotion']
print([s.name for s in loco.states])                # ['Idle', 'Walk', 'Run']
```

---

## See Also

- [`StateMachine`](StateMachine.md) -- returned by `add_state_machine()`
- [`load()`](load.md) -- load skeleton and animation assets
