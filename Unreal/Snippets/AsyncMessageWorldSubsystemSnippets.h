// Copyright Broken Rock Studios LLC. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "AsyncMessage.h"
#include "AsyncMessageHandle.h"
#include "AsyncMessageSystemBase.h"
#include "AsyncMessageSystemLogs.h"
#include "AsyncMessageWorldSubsystem.h"
#include "GameplayTagContainer.h"

namespace RockMessage
{
	// If you don't want to use this helper util.
	// Sys->QueueMessageForBroadcast(
	// 	FAsyncMessageId(MyGameplayTag),
	// 	FConstStructView::Make(MyStruct)
	// );
	template <typename T>
	void Broadcast(UWorld* World, FGameplayTag Channel, const T& Payload, TWeakPtr<FAsyncMessageBindingEndpoint> BindingEndpoint = nullptr)
	{
		auto AsyncMessageSystem = UAsyncMessageWorldSubsystem::GetSharedMessageSystem(World);
		if (!AsyncMessageSystem)
		{
			UE_LOG(LogAsyncMessageSystem, Error, TEXT("Broadcast failed to find message system for world"));
			return;
		}
		AsyncMessageSystem->QueueMessageForBroadcast(
			FAsyncMessageId(Channel),
			FConstStructView::Make(Payload),
			BindingEndpoint);
	}

	// If you don't want to use this helper util. 
	// TSharedPtr Sys = UAsyncMessageWorldSubsystem::GetSharedMessageSystem(GetWorld());
	// Sys->BindListener(FAsyncMessageId(MyGameplayTag),
	//                   TWeakObjectPtr(this),
	//                   &ThisClass::MyFunction);
	template <typename TOwner>
		requires std::is_base_of_v<UObject, TOwner>
	FAsyncMessageHandle RegisterListener(
		FGameplayTag Channel, TOwner* Object, void (TOwner::*Callback)(const FAsyncMessage&), const FAsyncMessageBindingOptions& Options = {},
		TWeakPtr<FAsyncMessageBindingEndpoint> BindingEndpoint = nullptr)
	{
		if (!Object)
		{
			UE_LOG(LogAsyncMessageSystem, Error, TEXT("RegisterListener called with null object for channel '%s'"), *Channel.ToString());
			return {};
		}
		auto AsyncMessageSystem = UAsyncMessageWorldSubsystem::GetSharedMessageSystem(Object->GetWorld());
		if (!AsyncMessageSystem)
		{
			UE_LOG(LogAsyncMessageSystem, Error, TEXT("RegisterListener failed to find message system for world"));
			return {};
		}
		return AsyncMessageSystem->BindListener(FAsyncMessageId(Channel), TWeakObjectPtr<TOwner>(Object), Callback, Options, BindingEndpoint);
	}
}
