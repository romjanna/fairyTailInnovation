from flask import Flask, render_template, request, jsonify
import openai
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

openai.api_key = "sk-proj-your-API-KEY"
openai_client = openai.OpenAI(api_key=openai.api_key)

# Function to get AI response with full conversation history
def get_step_response(model, messages):
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,  # Pass full conversation history
            top_p=0.95,  # More creativity but smooth frases
            max_tokens=300,  # Allow longer responses
            frequency_penalty=0.6,
            presence_penalty=1.3,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"Error API: {e}"

# Story Generation Function (Uses Parameters)
def generate_story(model, character, setting, lesson):
    # Create the initial prompt with parameters
    prompt_start = f"""
    You are a storyteller who writes engaging fairy tales for children.
    Use simple words suitable for children

    Write the **beginning** of a fairy tale with:
    - The protagonist is {character}.
    - The setting is {setting}.
    - The lesson to be taught is {lesson}.

    The opening **must introduce the hero and their challenge** in 2-3 sentences.
    The story **must start with** "Once upon a time..."
    """

    # Start conversation with AI
    messages = [{"role": "user", "content": prompt_start}]
    start = get_step_response(model, messages)

    print(f"\n🟢 **Story Start:** {start}")

    # Generate the Middle
    prompt_middle = f"""
    Continue the story based on what has happened so far.

    - Add **more details** about {character}'s adventure.
    - Introduce **a challenge** that {character} must overcome.
    - Use **3-4 sentences** to make the story more engaging.
    """

    # Append previous conversation
    messages.append({"role": "assistant", "content": start})
    messages.append({"role": "user", "content": prompt_middle})

    middle = get_step_response(model, messages)

    print(f"\n🟢 **Story Middle:** {middle}")

    # Generate the Ending
    prompt_end = f"""
    Now, finish the story.

    - How does {character} solve the challenge?
    - What is the lesson they learn?
    - End with a **clear moral** in 1 sentences.
    """

    # Append previous conversation
    messages.append({"role": "assistant", "content": middle})
    messages.append({"role": "user", "content": prompt_end})

    end = get_step_response(model, messages)

    print(f"\n🟢 **Story End:** {end}")

    # Return full story
    return f"{start}\n\n{middle}\n\n{end}"



# 🔹 Function to Generate and Display Image
def generate_and_show_image(main, setting, lesson):
    """Generates an image using OpenAI's DALL·E and displays it."""
    try:
        description = f"""
        Create an illustration inspired by a fairy tale.

        **Main theme**: {main}
        **Setting**: {setting}
        **Theme/Lesson**: {lesson}

        The illustration should visually represent the theme of the story in an engaging and imaginative way.
        Use **vibrant colors, rich textures, and a dreamlike atmosphere**.

        **Do NOT draw any text.**
        """
        # Request image generation
        response = openai_client.images.generate(
            model="dall-e-3",  # the latest model
            prompt=description,
            n=1,  # Number of images
            size="1024x1024"
        )

        # Extract the image URL
        image_url = response.data[0].url

        # Download the image from the URL
        image_response = requests.get(image_url)
        img = Image.open(BytesIO(image_response.content))

        # Display the image
        #display(img)

        return image_url  # Return URL for future use
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    character = data.get("character")
    setting = data.get("setting")
    lesson = data.get("lesson")

    #"ft:gpt-4o-mini-2024-07-18:kth::B6nrc1L8", "gpt-4o-mini-2024-07-18"
    story = generate_story("ft:gpt-4o-mini-2024-07-18:kth::B6nrc1L8", character, setting, lesson)
    image_url = generate_and_show_image(character, setting, lesson)

    return jsonify({"story": story, "image_url": image_url})

if __name__ == '__main__':
    app.run(debug=True)
