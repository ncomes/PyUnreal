# scene (module)

Module-level functions for querying and manipulating the current level.

## Import

```python
from pyunreal.scene import scene
```

## Functions

### scene.all()

Get all actors in the current level.

```python
actors = scene.all()
print(len(actors), "actors in level")
```

### scene.selected()

Get the currently selected actors.

```python
for actor in scene.selected():
    print(actor.name, actor.location)
```

### scene.select(actors_or_names)

Set the viewport selection. Accepts Actor wrappers, UE actors, or label strings.

```python
scene.select([actor1, actor2])
scene.select(['Chair_01', 'Table_01'])
```

### scene.find(name_pattern)

Find actors by glob pattern (case-insensitive).

```python
chairs = scene.find('Chair_*')
everything = scene.find('*Light*')
```

### scene.find_by_type(class_name)

Find actors by UE class name (case-insensitive).

```python
lights = scene.find_by_type('PointLight')
meshes = scene.find_by_type('StaticMeshActor')
```

### scene.find_by_tag(tag)

Find actors that have a specific tag.

```python
interactables = scene.find_by_tag('Interactive')
```
