// Copyright Broken Rock Studios LLC. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "ArcInventoryItemTypes.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ArcPlusInventoryRect.h"
#include "ArcPlusLibrary.generated.h"


class UArcItemStackModular;

/**
 * 
 */
UCLASS()
class ARCPLUS_API UArcPlusLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "ArcPlus")
	static int32 PackPosition(int32 Tab, int32 X, int32 Y, int32 Rotation);

	UFUNCTION(BlueprintCallable, Category = "ArcPlus")
	static void UnpackPosition(int32 packedValue, int32& Tab, int32& X, int32& Y, int32& Rotation);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "ArcPlus")
	static int32 GetTab(int32 packedValue);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "ArcPlus")
	static int32 GetX(int32 packedValue);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "ArcPlus")
	static int32 GetY(int32 packedValue);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "ArcPlus")
	static int32 GetRot(int32 packedValue);

	UFUNCTION(BlueprintCallable, BlueprintPure, Category = "ArcPlus")
	static int32 GetUnused(int32 packedValue);

	static FArcPlusInventoryRect MakeItemRectRef(const UArcItemStackModular* Item, const FArcInventoryItemSlotReference& Slot);
	static FArcPlusInventoryRect MakeItemRect(const UArcItemStackModular* Item, const FArcInventoryItemSlot& Slot);

};