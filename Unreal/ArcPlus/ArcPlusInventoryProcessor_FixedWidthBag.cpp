// Copyright Broken Rock Studios LLC. All Rights Reserved.

#include "ArcPlusInventoryProcessor_FixedWidthBag.h"

#include "ArcInventory.h"
#include "ArcPlus/ArcPlusLibrary.h"
#include "Helper/ArcPlusInventoryRect.h"

UArcPlusInventoryProcessor_FixedWidthBag::UArcPlusInventoryProcessor_FixedWidthBag()
	: bConsiderBagForLoot(true)
	  , BagLootPriority(0)
{
	BagSlotTags = ArcGameplayTags::FArcInvBagSlotTag.GetTag().GetSingleTagContainer();
}

TArray<FArcInventoryItemSlotReference> UArcPlusInventoryProcessor_FixedWidthBag::GetItemSlotReferences() const
{
	return BagSlots;
}

void UArcPlusInventoryProcessor_FixedWidthBag::OnInventoryBeginPlay_Implementation()
{
	// Only the server should create the bag slots
	if (GetOwnerRole() != ROLE_Authority)
	{
		return;
	}
	// We currently assume each custom inventory slot is it's own tab
	// But in the event we had more than 1 bag, we'd need to account for that, since each bag should have it's own tab id
	const uint32 CurrentMaxTab = GetOwningInventory()->CustomInventorySlots.Num();

	for (int32 y = 0; y < GridHeight; y++)
	{
		for (int32 x = 0; x < GridWidth; x++)
		{
			const uint32 SlotId = UArcPlusLibrary::PackPosition(CurrentMaxTab, x, y, 0);
			const FArcInventoryItemSlotReference ProxySlot(BagSlotTags, SlotId, GetOwningInventory());
			GetOwningInventory()->CreateInventorySlot(ProxySlot, Filter, EArcInventoryItemSlotReplicationFlags::Always);
			BagSlots.Add(ProxySlot);
		}
	}
}

void UArcPlusInventoryProcessor_FixedWidthBag::ProvideSlotAndWeightForLoot(
	TMap<FArcInventoryItemSlotReference, int>& SlotScores, UArcItemStackModular* ItemStack, FGameplayTag LootTag) const
{
	Super::ProvideSlotAndWeightForLoot(SlotScores, ItemStack, LootTag);

	if (bConsiderBagForLoot)
	{
		for (int32 i = 0; i < BagSlots.Num(); i++)
		{
			if (!IsValid(GetItemInSlot(BagSlots[i])))
			{
				auto& slotScore = SlotScores.FindOrAdd(BagSlots[i]);
				slotScore += BagSlots.Num() - i + BagLootPriority;
			}
		}
	}
}

EArcItemSlotAcceptance UArcPlusInventoryProcessor_FixedWidthBag::SlotAcceptsItem_Implementation(
	UArcItemStackModular* ItemStack, const FArcInventoryItemSlotReference& ToSlot, FArcInventoryItemSlotReference FromSlot,
	FGameplayTag Context) const
{
	// We don't want to be considered for 'swappable checks' as that is called every frame.
	if (Context.MatchesTag(ArcGameplayTags::Inventory_Action_SwappableCheck))
	{
		return EArcItemSlotAcceptance::DontCare;
	}
	if (!IsValid(ToSlot))
	{
		return EArcItemSlotAcceptance::No;
	}
	const FArcPlusInventoryRect ToRect = UArcPlusLibrary::MakeItemRectRef(ItemStack, ToSlot);
	
	if (!ToRect.IsWithinBounds(GridWidth, GridHeight))
	{
		return EArcItemSlotAcceptance::No;
	}
	TArray<UArcItemStackBase*> AllItems;
	FArcInventorySlotContainer slotContainer = GetOwningInventory()->GetSlotContainer();

	for (FArcInventoryItemSlot slot : slotContainer)
	{
		// If the item is null, we don't care about it. It's an empty slot.
		if (slot.ItemStack == nullptr)
		{
			continue;
		}
		
		UArcItemStackModular* modularItem = Cast<UArcItemStackModular>(slot.ItemStack);
		FArcPlusInventoryRect OtherRect = UArcPlusLibrary::MakeItemRect(modularItem, slot);
		if (ToRect.Overlaps(OtherRect))
		{
			return EArcItemSlotAcceptance::No;
		}
	}
	return Super::SlotAcceptsItem_Implementation(ItemStack, ToSlot, FromSlot, Context);
}

EArcInventoryProcessItemSlotResult UArcPlusInventoryProcessor_FixedWidthBag::ProcessItemSlotSwap_Implementation(
	UArcItemStackModular* SourceItem, FArcInventoryItemSlotReference FromSlot, UArcItemStackModular* DestItem, FArcInventoryItemSlotReference ToSlot,
	FGameplayTag Context)
{
	// We don't want to bother calculating things for 'swappable checks' as that is called every frame. Bags don't care about swappable checks.
	if (Context.MatchesTag(ArcGameplayTags::Inventory_Action_SwappableCheck))
	{
		return EArcInventoryProcessItemSlotResult::NotHandled;
	}
	if (!SourceItem)
	{
		UE_LOG(LogTemp, Warning, TEXT("ProcessItemSlotSwap: SourceItem is null"));
		return EArcInventoryProcessItemSlotResult::Rejected;
	}

	// If FromSlot is Invalid, then we are likely doing a 'pick up' from ground type operation.
	// We technically still are doing a 'Swap' operation, but the source item is not from a valid slot.
	const FArcPlusInventoryRect DestRect = UArcPlusLibrary::MakeItemRectRef(DestItem, FromSlot);
	const FArcPlusInventoryRect SourceRect = UArcPlusLibrary::MakeItemRectRef(SourceItem, ToSlot);

	if (!SourceRect.IsWithinBounds(GridWidth, GridHeight))
	{
		return EArcInventoryProcessItemSlotResult::Rejected;
	}
	if (!DestRect.IsWithinBounds(GridWidth, GridHeight))
	{
		return EArcInventoryProcessItemSlotResult::Rejected;
	}

	// Check for collisions with other items
	FArcInventorySlotContainer slotContainer = GetOwningInventory()->GetSlotContainer();
	for (const FArcInventoryItemSlot& slot : slotContainer)
	{
		// If the item is null, we don't care about it. It's an empty slot.
		if (slot.ItemStack == nullptr || slot.ItemStack == SourceItem || slot.ItemStack == DestItem)
		{
			continue;
		}
		const UArcItemStackModular* modularItem = Cast<UArcItemStackModular>(slot.ItemStack);
		FArcPlusInventoryRect OtherRect = UArcPlusLibrary::MakeItemRect(modularItem, slot);

		// Check if source item in new position would collide
		if (SourceRect.Overlaps(OtherRect))
		{
			return EArcInventoryProcessItemSlotResult::Rejected;
		}
		
		// Check if destination item in new position would collide
		if (DestRect.Overlaps(OtherRect))
		{
			return EArcInventoryProcessItemSlotResult::Rejected;
		}
	}
	return Super::ProcessItemSlotSwap_Implementation(SourceItem, FromSlot, DestItem, ToSlot, Context);
}
