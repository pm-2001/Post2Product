from utils.file_upload import s3fileUpload
import requests,io
import time

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {'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'}","language":'en',}
HUGGINGFACE_SPEECH_TO_TEXT_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

def query(payload, max_retries=10, retry_delay=30):
    retries = 0
    while retries < max_retries:
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        if response.status_code == 503:
            # Model is currently loading, wait and retry
            wait_time = retry_delay * (2 ** retries)
            print(f"Model is currently loading. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        elif response.status_code == 200:
            return response.content
        else:
            print("****************************************************")
            print(f"Error: {response.status_code}, {response.text}")
            return None
    
    print(f"Failed after {max_retries} retries.")
    return None

def generate_images_from_json(json_data):
# def generate_images_from_json(json_data):
    # db_history = Historys()
    new_json = {}
    for item in json_data:
        if item: 
            # item_name = next(iter(item))  # Get the key (item name) from the dictionary
            tags = json_data[item]  # Get the value (list of tags) from the dictionary  
            prompt = f"{item}: {', '.join(tags)}"
            image_bytes = query({"inputs": prompt})
            
            if image_bytes:
                try:
                    # image_link = save_image(image_bytes, item)
                    image = io.BytesIO(image_bytes)
                    image_link = s3fileUpload(image,item)
                    # print(image_link)

                    new_json[item] = {
                        "tags": ', '.join(tags),
                        "image_link": image_link
                    }

                except IOError:
                    print(f"Error: Could not generate image for {item}")
                    new_json[item] = {
                        "tags": ', '.join(tags),
                        "image_link": "Error: Image could not be generated"
                    }
        else:
            print(f"Error: Invalid item format in json_data: {item}")
    
    return new_json