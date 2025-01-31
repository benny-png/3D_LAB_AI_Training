# How to use large language model (LLM) and function calling in a Python script.

# https://ollama.com/

import ollama

def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a: OFF
        b:ON

    Returns:
        int: The sum of the two numbers.
    """
    # Explicitly cast inputs to integers
    a = int(a)
    b = int(b)
    answer = a + b
    print(f'{a} + {b} = {answer}')
    return answer


# Define the function
available_functions = {
    'add_two_numbers': add_two_numbers,
}

# Chat with Ollama
response = ollama.chat(
    model='llama3.2:1b',
    messages=[{'role': 'user', 'content': 'what is  twenty + 30? i want to know the answer very quickly'}],
    tools=[add_two_numbers],  # Pass the addition function
)


print(f"the response {response}")

# Execute the function if called by Ollama
for tool in response.message.tool_calls or []:
    function_to_call = available_functions.get(tool.function.name)
    print('Function to call:', function_to_call)
    if function_to_call:
        # Call the function with arguments provided by Ollama
        print('tool arguments:', tool.function.arguments)
        print('Function output:', function_to_call(**tool.function.arguments))
    else:
        print('Function not found:', tool.function.name)
