# AI Voice Control Interface

This project demonstrates an AI-powered voice control interface using various technologies such as Pygame, OpenCV, and speech recognition. The interface allows users to control an ESP32 LED/bulb using voice commands or text input.

## Features

- **Voice Recognition**: Uses Google Speech Recognition to capture and process voice commands.
- **Text-to-Speech (TTS)**: Converts text responses to speech using Kokoro TTS.
- **ESP32 Control**: Sends HTTP requests to control an ESP32 LED/bulb.
- **Video Playback**: Displays a video with a custom interface using Pygame and OpenCV.

## Technologies Used

- **Pygame**: For creating the graphical user interface and handling multimedia.
- **OpenCV**: For video processing and playback.
- **SpeechRecognition**: For capturing and recognizing voice commands.
- **Kokoro**: For text-to-speech conversion.
- **Requests**: For sending HTTP requests to the ESP32.
- **Soundfile**: For handling audio files.

## Setup

1. **Install Dependencies**:
    ```bash
    pip install pygame opencv-python numpy ollama requests SpeechRecognition kokoro soundfile
    ```

2. **Run the Application**:
    ```bash
    python main.py
    ```

## Usage

- **Start Voice Recognition**: Click the "Start Voice" button to begin listening for voice commands.
- **Stop Voice Recognition**: Click the "Stop Voice" button to stop listening for voice commands.
- **Send Text Command**: Type a command in the input box and click the "Send Text" button to process the command.

## Commands

- **Turn Light ON**: Say or type "Turn the light on".
- **Turn Light OFF**: Say or type "Turn the light off".

## File Structure

- `2_esp32_on_off_agent copy.py`: Main script containing the application logic.
- `assets/cool_ai_animation.mp4`: Video file displayed in the interface.

## License

This project is licensed under the MIT License.

## Acknowledgements

This project was prepared as part of a teaching session at 3D Lab about AI agency and function calling.
