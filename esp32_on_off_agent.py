import ollama
import requests

def control_esp_light(state: str) -> str:
    """
    Control the ESP32 LED/bulb state.

    Args:
        state: Either 'ON' or 'OFF' strictly to control the light

    Returns:
        str: Status message about the operation
    """
    ESP_IP = "192.168.0.249"  # Your ESP32's IP address
    
    try:
        if state.upper() == "ON":
            url = f"http://{ESP_IP}/H"
            response = requests.get(url)
            return "Light turned ON" if response.status_code == 200 else "Failed to turn light ON"
        elif state.upper() == "OFF":
            url = f"http://{ESP_IP}/L"
            response = requests.get(url)
            return "Light turned OFF" if response.status_code == 200 else "Failed to turn light OFF"
        else:
            return "Invalid state. Use 'ON' or 'OFF'"
    except requests.exceptions.RequestException as e:
        return f"Error communicating with ESP32: {str(e)}"

# Define the available functions
available_functions = {
    'control_esp_light': control_esp_light,
}

def process_command(user_input: str):
    """Process user command through LLM and execute light control"""
    response = ollama.chat(
        model='llama3.2:3b',  # or whichever model you're using
        messages=[{
            'role': 'user', 
            'content': f"{user_input}"
        }],
        tools=[control_esp_light],
    )

    print(f"LLM Response: {response}")

    # Execute the function if called by LLM
    for tool in response.message.tool_calls or []:
        function_to_call = available_functions.get(tool.function.name)
        if function_to_call:
            print(f"Executing: {tool.function.name} with args: {tool.function.arguments}")
            result = function_to_call(**tool.function.arguments)
            print(f"Result: {result}")
        else:
            print(f'Function not found: {tool.function.name}')

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter your command (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        process_command(user_input)