// Copyright Broken Rock Studios LLC. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Modular/ArcInventoryProcessor.h"
#include "ArcPlusInventoryProcessor_FixedWidthBag.generated.h"


// Fixed width of the bag
// Tarkov often has '4' wide.
// Factorio has '10 wide'
// Diablo had around 10-12.
// minecraft had 9 wide
// poe has 12 wide

/**
 * 
 */
UCLASS()
class LYRAGAME_API UArcPlusInventoryProcessor_FixedWidthBag : public UArcInventoryProcessor
{
	GENERATED_BODY()
public:
	
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory")
	int32 GridWidth = 4;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory")
	int32 GridHeight = 5;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory")
	FGameplayTagContainer BagSlotTags;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory")
	FArcInventoryItemSlotFilter Filter;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory", meta = (InlineCategoryProperty))
	bool bConsiderBagForLoot;
	//The loot priority of this bag.  The higher the number, the more likely a bag slot created by this processor will be chose in LootItem.  
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ArcPlus|Inventory", meta=(EditCondition="bConsiderBagForLoot", EditConditionHides))
	int32 BagLootPriority;
	
	UPROPERTY()
	TArray<FArcInventoryItemSlotReference> BagSlots;

	UArcPlusInventoryProcessor_FixedWidthBag();
	
	UFUNCTION(BlueprintCallable)
	TArray<FArcInventoryItemSlotReference> GetItemSlotReferences() const;

	virtual void OnInventoryBeginPlay_Implementation() override;
	virtual void ProvideSlotAndWeightForLoot(TMap<FArcInventoryItemSlotReference, int>& SlotScores, UArcItemStackModular* ItemStack, FGameplayTag LootTag) const override;
	virtual EArcItemSlotAcceptance SlotAcceptsItem_Implementation(UArcItemStackModular* ItemStack, const FArcInventoryItemSlotReference& Slot, FArcInventoryItemSlotReference FromSlot, FGameplayTag Context) const override;
	virtual EArcInventoryProcessItemSlotResult ProcessItemSlotSwap_Implementation(UArcItemStackModular* SourceItem, FArcInventoryItemSlotReference FromSlot, UArcItemStackModular* DestItem, FArcInventoryItemSlotReference ToSlot, FGameplayTag Context) override;
};
