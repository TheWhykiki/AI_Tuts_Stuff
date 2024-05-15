import sys
import os
import requests

############################################################################################################
"""
Konfiguration / Settings
"""
############################################################################################################

# Konfiguration
#api_key = 'YOUR_API_KEY'

#Standard endpoint for chat
#Through model gpt-4o but without direct call to Vision API
chatgpt_endpoint = 'https://api.openai.com/v1/chat/completions'
model_name = 'gpt-4o'
num_images = 3 # Number of images in the directory to be imported
image_src_name = 'sample' # Name of the image -> your images should be named sample-1.jpg, sample-3.jpg, ... (or png)
img_type = 'png' # file type of the images (png or jpg)
base_url = 'http://youtube.thewhykiki.de/2024-05-14__GPT-4o_WebUI_Generator/source-images/' # Path to the directory with the images
output_folder_base = 'generator_output'  # local directory for the output of the generated images
output_folder_images = f'{output_folder_base}/images'  # Directory for the output of the generated images

#Endpoint for Image Generation
image_gen_endpoint = 'https://api.openai.com/v1/images/generations'
image_model_name = 'dall-e-3'


############################################################################################################
"""
The most important thing: the respective system prompts.
analysis_prompt is the system prompt for analyzing the images and generating the HTML code
image_gen_prompt is the system prompt for generating the images based on text descriptions
The Python code is still important for the whole thing to work. But that will change...
Function Calling will soon make it possible for an LLM to actually execute all programs itself.
"""
############################################################################################################

analysis_prompt = (
    "You are WebUIAnalyzer GPT, an expert in the creation and analysis of websites. Your expertise includes HTML, JS, and CSS. You are tasked with precisely analyzing website screenshots. Based on the provided image, create clean, formatted HTML code. Thoroughly analyze the image and create HTML that matches the structure and content of the image. Also, identify any content images contained therein and describe them in clear, precise bullet points. You must determine from the screenshot whether they are HTML elements or images used in HTML, such as article images, hero images, etc."
    "Analyze the content image and create a short description of the image such as 'Man at computer with blurred background, image is in wide format.' Your image description should be added at the end of the HTML in a script block as a JSON object. For each image description, also specify the image format, such as wide, square, etc. Each image gets a unique ID starting with 1 and a description. The JSON object should then look like this:"
    "<json>"
    "[{"
    "'id': 1,"
    "'description': 'Man at computer with blurred background, image is in wide format'"
    "},"
    "{"
    "'id': 2,"
    "'description': 'Computer keyboard in close-up, square image'"
    "}]"
    "</json>"
    "If there are no images within the analyzed website screenshot or you cannot identify any, then the JSON object should only contain 'No images found.'"
    "You may not consult external sources and should use no unsafe or inaccurate data. Ensure that the HTML code is well-structured and conforms to modern web standards. The required CSS will be included as inline CSS in the head of the HTML."
    "Your response is always valid HTML, which always starts with <html> and ends with </html>. You must not violate this rule."
    "Describe images exclusively in bullet points. You must not deviate from the topic, repeat information, or include unnecessary details. Your focus is solely on analyzing the screenshot and creating code. Add a script block at the end of the HTML code containing the descriptions of the identified images in JSON format."
    "You analyze accurately and step-by-step how the content and UI of the website on the screenshot look and create exactly that as HTML. Do not create any dummy content, and you will not omit any areas. Your goal and task are to transform the content of the screenshot as precisely as possible into valid HTML. Do not invent any texts or headlines, but reproduce exactly what you have seen in a detailed examination of the website screenshot."
    "You respond exclusively in valid HTML; your response must always begin with <html> and end with </html>. Do not explain anything; your answer consists only of the desired code."
)

image_gen_prompt = (
    "You are ImageGenerator GPT, specialized in creating high-quality images based on text descriptions. "
    "Your task is to generate an image that precisely visualizes the elements of the given description. "
    "Consider specific formatting requirements such as 'wide', 'square', or others that describe the image format. "
    "Ensure the image is creative and thematically aligned with the description and specified format. "
    "Avoid any blurry or irrelevant depictions and focus exclusively on the given description."
)



############################################################################################################
"""
Checks whether the specified directory exists and creates it if it does not.
:param directory: The path of the directory to be checked.
"""
############################################################################################################
def check_and_create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory created: {directory}")
    else:
        print(f"Directory already exists: {directory}")


############################################################################################################
"""
Generates a dictionary with the image URLs based on the number of images and the image name '-URL.
and the base URL.
"""
############################################################################################################
def get_image_urls():
    image_urls = []
    for i in range(1, num_images + 1):
        image_url = f"{base_url}{image_src_name}-{i}.{img_type}"
        print(f"Generated URL: {image_url}")
        image_urls.append(image_url)
    return image_urls


############################################################################################################
"""
Sends the image URL to the ChatGPT API for processing and returns the response.
:param image_url: The URL of the image to be analyzed.
:return: The response from the ChatGPT API.
"""
############################################################################################################
def send_image_to_chatgpt(image_url):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": analysis_prompt},
            {"role": "user", "content": image_url}
        ]
    }
    response = requests.post(chatgpt_endpoint, headers=headers, json=data)
    print("Receive response from the ChatGPT API:")
    print(response.json())
    return response.json()



############################################################################################################
"""
Creates an HTML file based on the content received.
param html_content: The HTML content to be written to the file.
:param file_number: The number of the file used to name the file.
:return: The path of the created HTML file.
"""
############################################################################################################
def create_html_file(html_content, file_number):
    file_path = f"{output_folder_base}/sample-{file_number:02}.html"
    with open(file_path, "w") as file:
        file.write(html_content)
    print(f"HTML file saved: {file_path}")
    return file_path



############################################################################################################
"""
Generates an image based on the given prompt and saves it.
:param prompt: The prompt used to generate the image.
:param file_number: The number of the file used to name the file.
:return: The path of the generated image or None if no image was generated.
"""
############################################################################################################
def generate_image_from_prompt(prompt, file_number):
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {"model": image_model_name, "prompt": f"{image_gen_prompt} {prompt}"}
    response = requests.post(image_gen_endpoint, headers=headers, json=data)
    print("Receive response from the image generation API:")
    print(response.json())
    if response.status_code == 200 and 'image' in response.json():
        image_data = response.json()['image']
        image_path = f"{output_folder_images}/sample-{file_number:02}-image-{file_number:02}.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(base64.b64decode(image_data))
        print(f"Image generated and saved: {image_path}")
        return image_path
    else:
        print("Error: No picture in the answer.")
        return None



############################################################################################################
"""
Main function for controlling the process. It starts the script, checks and creates required directories,
sends image URLs to the ChatGPT API for processing and generates HTML files based on the responses received.
"""
############################################################################################################
def main():
    print("Start the script...")
    check_and_create_directory(output_folder_base)
    check_and_create_directory(output_folder_images)
    image_urls = get_image_urls()
    print(f"Image URLs: {image_urls}")
    if not image_urls:
        print("No images found. Please check the list 'image_urls'.")
        sys.exit()
    for idx, image_url in enumerate(image_urls):
        print(f"Verarbeite Bild-URL: {image_url}")
        response = send_image_to_chatgpt(image_url)
        if 'choices' in response and response['choices']:
            html_content = response['choices'][0]['message']['content']
            print("Get HTML content. Create HTML file...")
            html_file_path = create_html_file(html_content, idx)
        else:
            print("No valid response for image. Check the API response and request.")

if __name__ == "__main__":
    main()