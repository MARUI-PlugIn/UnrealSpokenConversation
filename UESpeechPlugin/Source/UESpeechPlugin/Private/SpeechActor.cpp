// Fill out your copyright notice in the Description page of Project Settings.


#include "SpeechActor.h"

#include <string>
#include "Logging/MessageLog.h"
#include "HAL/UnrealMemory.h"
#include "Kismet/GameplayStatics.h"
#include "Components/TextRenderComponent.h"

// Sets default values
ASpeechActor::ASpeechActor()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	// PrimaryActorTick.bCanEverTick = true;
}

// Called when the game starts or when spawned
void ASpeechActor::BeginPlay()
{
	Super::BeginPlay();
	
	this->AudioCapture = Cast<UAudioCaptureComponent>(
		AddComponentByClass(UAudioCaptureComponent::StaticClass(), false, FTransform::Identity, false)
	);
	this->Submix = NewObject<USoundSubmix>();
	this->AudioCapture->SoundSubmix = this->Submix;

	ISocketSubsystem* socksys = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
	this->Socket = socksys->CreateSocket(NAME_Stream, TEXT("default"), false);
	FIPv4Address ip;
	FIPv4Address::Parse(TEXT("127.0.0.1"), ip);
	TSharedRef<FInternetAddr> internetAddr = socksys->CreateInternetAddr();
	internetAddr->SetIp(ip.Value);
	internetAddr->SetPort(65432);

	if (!this->Socket->Connect(*internetAddr)) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Failed to connect to localhost"));
		return;
	}
	
	


}

// Called every frame
void ASpeechActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}

void ASpeechActor::SetDisplayText(FString Text)
{
	if (this->DisplayText) {
		UTextRenderComponent* TextComponent = this->DisplayText->GetTextRender();
		if (TextComponent) {
			TextComponent->SetText(FText::FromString(Text));
		}
	}
}

void ASpeechActor::startTalking(Speech_Result& Result)
{
	AudioCapture->Start();
	Audio::FMixerDevice* MixerDevice = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(GetWorld());
	MixerDevice->RegisterSoundSubmix(Submix);
	MixerDevice->StartRecording(Submix, 0);
	Submix->SetSubmixOutputVolume(GetWorld(), 0);
	this->SetDisplayText(TEXT("Hold <Space> and talk,\nrelease when finished."));
	Result = Speech_Result::Then;
}

void ASpeechActor::stopTalking(Speech_Result& Result)
{
	float Channels;
	float SampleRate;
	Audio::FMixerDevice* MixerDevice = FAudioDeviceManager::GetAudioMixerDeviceFromWorldContext(GetWorld());
	Audio::FAlignedFloatBuffer InBuffer = MixerDevice->StopRecording(Submix, Channels, SampleRate);
	
	float* InData = InBuffer.GetData();
	int32 InDataSize = InBuffer.Num() * sizeof(float);
	UE_LOG(LogTemp, Warning,
		TEXT("SpeechActor: Recorded %i bytes of audio. Channels=%f, SampleRate=%f"),
		InDataSize, Channels, SampleRate
	)
	if (InDataSize > 0) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: First sample=%f"), InData[0]);
	}
	this->SetDisplayText(TEXT("Resampling..."));
	// resample 48000 to 16000 and 2 channels to 1 channel, and amplify
	float MaxVal = 0;
	Audio::FAlignedFloatBuffer Buffer;
	Buffer.SetNum((InBuffer.Num() / 3) / 2);
	UE_LOG(LogTemp, Warning, TEXT("Resampling from %i samples (48k stereo) to %i samples (16k mono)"), InBuffer.Num(), Buffer.Num());
	int32 DataSize = Buffer.Num() * sizeof(float);
	float* Data = Buffer.GetData();
	for (int i = Buffer.Num() - 1; i >= 0; i--) {
		float fi = 0;
		for (int k = 5; k >= 0; k--) {
			fi += InData[i * 2 * 3 + k];
		}
		Buffer[i] = fi;
		MaxVal = fmaxf(MaxVal, fi);
	}
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: MaxVal=%f"), MaxVal);
	for (int i = Buffer.Num() - 1; i >= 0; i--) {
		Data[i] = Data[i] / MaxVal;
	}
	// this->Socket->SetNonBlocking(false);

	this->SetDisplayText(TEXT("Sending audio to server..."));
	int32 BytesTransferred;
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Sending data size..."));
	BytesTransferred = 0;
	if (!this->Socket->Send((uint8*)&DataSize, sizeof(int32), BytesTransferred) || BytesTransferred != 4) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Failed to send data size"));
		Result = Speech_Result::Error;
		return;
	}
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Sending data..."));
	BytesTransferred = 0;
	if (!this->Socket->Send((uint8*)Data, DataSize, BytesTransferred) || BytesTransferred != DataSize) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Failed to send data"));
		Result = Speech_Result::Error;
		return;
	}

	this->SetDisplayText(TEXT("Waiting for reply from server..."));
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Receiving data size..."));
	BytesTransferred = 0;
	if (!Socket->Recv((uint8*)&DataSize, 4, BytesTransferred, ESocketReceiveFlags::WaitAll) || BytesTransferred != 4) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Failed to receive data size"));
		return;
	}
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Receiving %i bytes of data..."), DataSize);
	Buffer.SetNum(DataSize / sizeof(float));
	Data = Buffer.GetData();
	BytesTransferred = 0;
	if (!Socket->Recv((uint8*)Data, DataSize, BytesTransferred, ESocketReceiveFlags::WaitAll) || BytesTransferred != DataSize) {
		UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Failed to receive data"));
		return;
	}
	UE_LOG(LogTemp, Warning, TEXT("SpeechActor: Successfully receiveed data."));

	this->SetDisplayText(TEXT("Starting audio playback..."));
	Audio::FSampleBuffer SampleBuffer(Buffer, 1, 16000);
	Audio::FSoundWavePCMWriter Writer;
	USoundWave* SoundWave = Writer.SynchronouslyWriteSoundWave(SampleBuffer);
	UGameplayStatics::PlaySound2D(GetWorld(), SoundWave);

	this->SetDisplayText(TEXT("Press and hold <Space> to talk"));
	Result = Speech_Result::Then;
}

