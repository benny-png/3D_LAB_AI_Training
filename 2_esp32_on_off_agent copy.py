import pygame
import pygame.mixer
import cv2
import numpy as np
import ollama
import requests
import speech_recognition as sr
from kokoro import KPipeline
import soundfile as sf
import threading
import os
from queue import Queue

# Initialize video first to get dimensions
video = cv2.VideoCapture('assets/cool_ai_animation.mp4')
video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# Calculate the best window size while maintaining aspect ratio
VIDEO_DISPLAY_HEIGHT = 600
scale_factor = VIDEO_DISPLAY_HEIGHT / video_height
VIDEO_DISPLAY_WIDTH = int(video_width * scale_factor)

# Add padding for controls
PADDING = 150
SCREEN_WIDTH = VIDEO_DISPLAY_WIDTH
SCREEN_HEIGHT = VIDEO_DISPLAY_HEIGHT + PADDING

print(f"Original video dimensions: {video_width}x{video_height}")
print(f"Display dimensions: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Initialize Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Voice Control Interface")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
button_font = pygame.font.Font(None, 36)
input_font = pygame.font.Font(None, 32)
status_font = pygame.font.Font(None, 28)

# Button dimensions
button_height = 50
button_width = 150
button_y = SCREEN_HEIGHT - 60

# UI Elements positioning
START_BUTTON = pygame.Rect(SCREEN_WIDTH//4 - 180, button_y, button_width, button_height)
STOP_BUTTON = pygame.Rect(SCREEN_WIDTH//4, button_y, button_width, button_height)
SEND_BUTTON = pygame.Rect(SCREEN_WIDTH//4 + 180, button_y, button_width, button_height)
INPUT_BOX = pygame.Rect(20, button_y - 60, SCREEN_WIDTH - 40, 40)

# Video position
video_x = (SCREEN_WIDTH - VIDEO_DISPLAY_WIDTH) // 2
video_y = 0

# Initialize Speech Recognition and TTS
recognizer = sr.Recognizer()
pipeline = KPipeline(lang_code='a')

# Global state
is_listening = False
current_command = ""
current_status = "Ready"
input_text = ""
input_active = False
command_queue = Queue()

def speak(text):
    """Convert text to speech using Kokoro TTS"""
    try:
        generator = pipeline(text, voice='af_bella', speed=1)
        for _, _, audio in generator:
            temp_file = 'temp_speech.wav'
            sf.write(temp_file, audio, 24000)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            if os.path.exists(temp_file):
                os.remove(temp_file)
    except Exception as e:
        print(f"TTS Error: {e}")

def control_esp_light(state: str) -> str:
    """Control the ESP32 LED/bulb state"""
    ESP_IP = "192.168.0.249"
    
    try:
        if state.upper() == "ON":
            url = f"http://{ESP_IP}/H"
            response = requests.get(url)
            result = "Light turned on boss Benjamin!" if response.status_code == 200 else "Failed to turn light ON"
        elif state.upper() == "OFF":
            url = f"http://{ESP_IP}/L"
            response = requests.get(url)
            result = "Light turned off boss Benjamin!" if response.status_code == 200 else "Failed to turn light OFF"
        else:
            result = "Invalid state. Use 'ON' or 'OFF'"
        return result
    except requests.exceptions.RequestException as e:
        return f"Error communicating with ESP32: {str(e)}"

def process_command_thread():
    """Process commands from the queue"""
    global current_status
    while True:
        user_input = command_queue.get()
        if user_input is None:  # Sentinel value to stop the thread
            break
            
        current_status = "Processing command..."
        
        try:
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[{
                    'role': 'user', 
                    'content': f"Command: {user_input}. Determine if this is a request to turn the light ON or OFF. " +
                              "Only call control_esp_light with 'ON' or 'OFF'. If uncertain, don't call the function."
                }],
                tools=[control_esp_light],
            )

            for tool in response.message.tool_calls or []:
                if tool.function.name == 'control_esp_light':
                    result = control_esp_light(**tool.function.arguments)
                    current_status = result
                    threading.Thread(target=speak, args=(result,)).start()
                    break
            else:
                current_status = "I'm not sure what you want me to do with the light"
                threading.Thread(target=speak, args=(current_status,)).start()
                
        except Exception as e:
            current_status = f"Error processing command: {str(e)}"
            threading.Thread(target=speak, args=(current_status,)).start()

def listen_for_command():
    """Listen for voice input in a separate thread"""
    global current_command, current_status, is_listening
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while is_listening:
            try:
                current_status = "Listening..."
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                current_status = "Processing..."
                
                command = recognizer.recognize_google(audio)
                current_command = command
                current_status = f"Command: {command}"
                
                command_queue.put(command)
                
            except sr.WaitTimeoutError:
                current_status = "No speech detected"
            except sr.UnknownValueError:
                current_status = "Could not understand audio"
            except Exception as e:
                current_status = f"Error: {str(e)}"

def main():
    global is_listening, current_command, current_status, input_text, input_active
    
    # Start the command processing thread
    processing_thread = threading.Thread(target=process_command_thread)
    processing_thread.daemon = True
    processing_thread.start()
    
    listen_thread = None
    background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    background.fill(BLACK)
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Handle video playback
        success, video_image = video.read()
        if success:
            video_surf = pygame.image.frombuffer(
                cv2.cvtColor(video_image, cv2.COLOR_BGR2RGB).tobytes(), 
                video_image.shape[1::-1], 
                "RGB"
            )
            video_surf = pygame.transform.scale(video_surf, (VIDEO_DISPLAY_WIDTH, VIDEO_DISPLAY_HEIGHT))
        else:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            
        # Draw background and video
        screen.blit(background, (0, 0))
        screen.blit(video_surf, (video_x, video_y))
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if START_BUTTON.collidepoint(mouse_pos) and not is_listening:
                    is_listening = True
                    current_status = "Starting voice recognition..."
                    listen_thread = threading.Thread(target=listen_for_command)
                    listen_thread.start()
                elif STOP_BUTTON.collidepoint(mouse_pos) and is_listening:
                    is_listening = False
                    current_status = "Stopped voice recognition"
                    if listen_thread:
                        listen_thread.join()
                elif SEND_BUTTON.collidepoint(mouse_pos) and input_text:
                    command_queue.put(input_text)
                    input_text = ""
                
                input_active = INPUT_BOX.collidepoint(mouse_pos)
                
            elif event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN and input_text:
                        command_queue.put(input_text)
                        input_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        # Draw interface elements
        pygame.draw.rect(screen, WHITE if input_active else GRAY, INPUT_BOX, 2)
        text_surface = input_font.render(input_text, True, WHITE)
        text_rect = text_surface.get_rect(topleft=(INPUT_BOX.x + 5, INPUT_BOX.y + 5))
        screen.blit(text_surface, text_rect)

        if not input_text and not input_active:
            placeholder = input_font.render("Type your command here...", True, GRAY)
            screen.blit(placeholder, (INPUT_BOX.x + 5, INPUT_BOX.y + 5))

        for button, text, color in [
            (START_BUTTON, "Start Voice", BLUE if not is_listening else GRAY),
            (STOP_BUTTON, "Stop Voice", RED if is_listening else GRAY),
            (SEND_BUTTON, "Send Text", GREEN if input_text else GRAY)
        ]:
            pygame.draw.rect(screen, color, button, border_radius=10)
            text_surf = button_font.render(text, True, WHITE)
            text_rect = text_surf.get_rect(center=button.center)
            screen.blit(text_surf, text_rect)

        status_bg = pygame.Rect(10, button_y - 100, SCREEN_WIDTH - 20, 30)
        pygame.draw.rect(screen, BLACK, status_bg)
        status_text = status_font.render(current_status, True, WHITE)
        screen.blit(status_text, (20, button_y - 95))

        pygame.display.flip()
        clock.tick(fps)

    # Cleanup
    command_queue.put(None)  # Signal the processing thread to stop
    if processing_thread:
        processing_thread.join()
    video.release()
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")