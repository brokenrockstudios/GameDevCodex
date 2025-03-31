// Copyright Broken Rock Studios LLC. All Rights Reserved.

#include "ArcPlusInventoryRect.h"

FArcPlusInventoryRect::FArcPlusInventoryRect(): Position(0, 0), Size(1, 1)
{
}

FArcPlusInventoryRect::FArcPlusInventoryRect(const FIntPoint& InPosition, const FIntPoint& InSize): Position(InPosition), Size(InSize)
{
}

int32 FArcPlusInventoryRect::Left() const
{
	return Position.X;
}

int32 FArcPlusInventoryRect::Right() const
{
	return Position.X + Size.X;
}

int32 FArcPlusInventoryRect::Top() const
{
	return Position.Y;
}

int32 FArcPlusInventoryRect::Bottom() const
{
	return Position.Y + Size.Y;
}

bool FArcPlusInventoryRect::HasPositiveArea() const
{
	return Size.X > 0 && Size.Y > 0;
}

bool FArcPlusInventoryRect::Overlaps(const FArcPlusInventoryRect& Other) const
{
	if (!HasPositiveArea() || !Other.HasPositiveArea())
	{
		return false;
	}
	return Left() < Other.Right() &&
		Right() > Other.Left() &&
		Top() < Other.Bottom() &&
		Bottom() > Other.Top();
}

bool FArcPlusInventoryRect::IsWithinBounds(int32 GridWidth, int32 GridHeight) const
{
	return Position.X >= 0 &&
		Position.Y >= 0 &&
		Right() <= GridWidth &&
		Bottom() <= GridHeight;
}

FString FArcPlusInventoryRect::ToString() const
{
	return FString::Printf(TEXT("Position: (%d, %d), Size: (%d, %d)"), Position.X, Position.Y, Size.X, Size.Y);
}
