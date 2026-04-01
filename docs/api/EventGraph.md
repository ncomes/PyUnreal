---
description: "EventGraph API reference — programmatic Blueprint EventGraph node creation, pin wiring, and variable setup in Unreal Engine Python."
---

# EventGraph

Wrapper for programmatic EventGraph node creation and pin wiring.

Requires the PyUnrealBridge or MCA Editor C++ plugin.

## Import

```python
from pyunreal.anim import AnimBlueprint, EventGraph, GraphNode
```

## Access

Get the EventGraph from any Blueprint or AnimBlueprint:

```python
abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')
eg = abp.event_graph

# Also works on regular Blueprints:
from pyunreal.blueprint import Blueprint
bp = Blueprint.load('/Game/Blueprints/BP_Player')
eg = bp.event_graph
```

## EventGraph Methods

### add_event(event_name)

Add an event node (e.g. `BlueprintInitializeAnimation`, `ReceiveBeginPlay`).

```python
init = eg.add_event('BlueprintInitializeAnimation')
update = eg.add_event('BlueprintUpdateAnimation')
```

Returns a `GraphNode`.

### add_call(function_name, target_class='')

Add a function call node. Searches the Blueprint's class hierarchy and common engine classes.

```python
pawn = eg.add_call('TryGetPawnOwner')
vel = eg.add_call('GetVelocity', target_class='Actor')
```

### add_cast(target_class)

Add a Cast To node.

```python
cast = eg.add_cast('WCompanionCharacter')
```

### add_variable_get(var_name)

Add a variable GET node.

```python
speed_get = eg.add_variable_get('Speed')
```

### add_variable_set(var_name)

Add a variable SET node.

```python
speed_set = eg.add_variable_set('Speed')
```

### nodes

List all nodes in the EventGraph.

```python
for node in eg.nodes:
    print(node['id'], node['class'], node['title'])
```

## GraphNode

Lightweight wrapper returned by `add_*` methods.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | str | Unique node GUID |
| `label` | str | Human-readable name |
| `pins` | list[dict] | Pin info: direction, name, type |

### connect(source_pin, target_node, target_pin)

Wire an output pin to another node's input pin.

```python
init.connect('then', pawn, 'execute')
pawn.connect('ReturnValue', cast, 'Object')
cast.connect('CastSucceeded', set_char, 'execute')
```

Returns self for chaining.

### set_position(x, y)

Position the node in the graph editor.

```python
init.set_position(0, 0)
pawn.set_position(300, 0)
```

## Full Example: AnimBP EventGraph

```python
from pyunreal.anim import AnimBlueprint

abp = AnimBlueprint.load('/Game/AnimBP/ABP_Character')
eg = abp.event_graph

# Initialize Animation — get pawn, cast, cache references
init = eg.add_event('BlueprintInitializeAnimation')
pawn = eg.add_call('TryGetPawnOwner')
cast = eg.add_cast('WCompanionCharacter')
set_char = eg.add_variable_set('Character')
get_move = eg.add_call('GetCharacterMovement')
set_move = eg.add_variable_set('MovementComponent')

# Wire the initialization chain
init.connect('then', pawn, 'execute')
pawn.connect('then', cast, 'execute')
cast.connect('CastSucceeded', set_char, 'execute')
set_char.connect('then', get_move, 'execute')
get_move.connect('then', set_move, 'execute')

# Data connections
cast.connect('As WCompanionCharacter', set_char, 'Character')
cast.connect('As WCompanionCharacter', get_move, 'self')
get_move.connect('ReturnValue', set_move, 'MovementComponent')

# Layout nodes for readability
init.set_position(0, 0)
pawn.set_position(300, 0)
cast.set_position(600, 0)
set_char.set_position(900, 0)
get_move.set_position(1200, 0)
set_move.set_position(1500, 0)

abp.compile()
```
