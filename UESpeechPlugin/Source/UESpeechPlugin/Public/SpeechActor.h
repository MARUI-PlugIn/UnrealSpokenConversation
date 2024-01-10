// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioCaptureComponent.h"
#include "AudioDevice.h"
#include "AudioMixerDevice.h"
#include "AudioDeviceManager.h"

#include "SocketSubsystem.h"
#include "Interfaces/IPv4/IPv4Address.h"
#include "IPAddress.h"
#include "Sockets.h"
#include "HAL/RunnableThread.h"
#include "Async/Async.h"

#include "SpeechActor.generated.h"

UENUM(BlueprintType)
enum class Speech_Result : uint8
{
	Then, Error
};

UCLASS()
class UESPEECHPLUGIN_API ASpeechActor : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ASpeechActor();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;

	FSocket* Socket;
	UAudioCaptureComponent* AudioCapture;
	USoundSubmix* Submix;

public:
	// Called every frame
	virtual void Tick(float DeltaTime) override;


	UFUNCTION(BlueprintCallable, Category = "Speech", Meta = (DisplayName = "Start Taking", ExpandEnumAsExecs = "Result"))
	void startTalking(Speech_Result& Result);

	UFUNCTION(BlueprintCallable, Category = "Speech", Meta = (DisplayName = "Stop Taking", ExpandEnumAsExecs = "Result"))
	void stopTalking(Speech_Result& Result);
};
