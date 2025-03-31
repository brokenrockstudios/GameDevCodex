// Copyright Broken Rock Studios LLC. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"

#include "ArcPlusInventoryRect.generated.h"

// Define a structure to represent an item's position and size in the grid
USTRUCT()
struct LYRAGAME_API FArcPlusInventoryRect
{
	GENERATED_BODY()

	FIntPoint Position;
	FIntPoint Size;

	FArcPlusInventoryRect();
	FArcPlusInventoryRect(const FIntPoint& InPosition, const FIntPoint& InSize);

	int32 Left() const;
	int32 Right() const;
	int32 Top() const;
	int32 Bottom() const;

	bool HasPositiveArea() const;
	bool Overlaps(const FArcPlusInventoryRect& Other) const;
	bool IsWithinBounds(int32 GridWidth, int32 GridHeight) const;
	FString ToString() const;
};
