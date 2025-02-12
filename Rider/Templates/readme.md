
In Rider you can create your own file templates for quicker file creation.

Rider already includes Actor, ActorComponent, Character, Empty, Pawn, Interface, and many others.

They don't have one for Structs or Enums for some reason.

1. Go to Settings -> Editor -> File Templates -> Unreal Engine
2. In top right click the +
3. Set the default file name and description
4. Group should be "Unreal Engine"

Use one of these templates
* [UStruct](Struct.h)
* [UEnum](Enum.h)


## Bonus tips

Rider IDE doesn't allow manually editing/creating the cpp.
It is partially automated by referencing the Unreal Engine installed location
e.g. `C:\Program Files\Epic Games\UE_5.5\Engine\Content\Editor\Templates`
There you will find things like ActorClass.h.template and ActorClass.cpp.template

You can add your own there.

