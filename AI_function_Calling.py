from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf

# Initialize the TTS pipeline
pipeline = KPipeline(lang_code='a')  # American English

# Define the add_two_numbers function
def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers and generate reflective feedback via hardcoded TTS.

    Args:
        a: The first integer number.
        b: The second integer number.

    Returns:
        int: The sum of the two numbers.
    """
    # Perform the addition
    a = int(a)
    b = int(b)
    answer = a + b
    
    # Hardcoded feedback message
    feedback_message = f""" From my calculation, the sum of {a} and {b} is {answer}.
    """
    
    # Generate the audio for the feedback message using Kokoro TTS
    generator = pipeline(feedback_message, voice='af_bella', speed=1, split_pattern=r'\n+')
    for i, (gs, ps, audio) in enumerate(generator):
        print(i)  # index of current iteration
        print(gs)  # graphemes/text
        print(ps)  # phonemes
        display(Audio(data=audio, rate=24000, autoplay=True))  # Play the audio
        sf.write(f'feedback_{i}.wav', audio, 24000)  # Save the audio file

    return answer

# Example of calling the add_two_numbers function
result = add_two_numbers(20, 30)

# Print the result
print(f"Result of adding 20 and 30: {result}")
