# UnrealSpokenConversation

A UnrealEngine plugin and Python server for spoken conversation inside Unreal Engine.
The plugin records audio input from the microphone and sends the audio data to the Python server via local socket.
The Python server receives the audio data and performs three operations: audio transcription (speech-to-text / voice recognition), text response generation (text generation), and voice synthesis (text-to-speech).
The AI models for these three tasks are downloaded automatically from huggingface and run locally.

## Requirements

- Python 3
- Unreal Engine

## How to use

(1) Run the server. The server takes one argument: `en` for English speech processing, `de` for German speech processing.
```
python main.py en
```
(2) Add the `SpeechActor` to your Unreal level. Call its `startTaking` function (via Blueprint or C++).
(3) Speak.
(4) When finished speaking, call the `stopTalking` function of `SpeechActor` .

The audio data is then processed in the Python server. Check the console output of the server to see the text recognition and response. The server will send the response as WAV audio to `SpeechActor` which will play it as a sound in the level.


