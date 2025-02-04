import ollama
from ollama import generate

import glob
import pandas as pd
from PIL import Image

import os
from io import BytesIO

def load_or_create_dataframe(filename):
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=['image_file', 'description'])
    return df
df = load_or_create_dataframe('image_descriptions.csv')

# print(glob.glob('./images/1.*'))

def get_images(folder_path):
    return glob.glob(f"{folder_path}/*.jpg")

image_paths = get_images('./images')
image_paths = image_paths[:1]
image_paths.sort()

print(image_paths)

def process_image(image_file):
    print(f"\nProcessing {image_file}\n")
    with Image.open(image_file) as img:
        with BytesIO() as buffer:
            img.save(buffer, format='JPEG')
            image_bytes = buffer.getvalue()

    full_response = ''
    # generate image description
    for response in generate(model = 'llava', prompt='describe this image and make sure to include anything notable about it (include text you see in the image):',
                             images=[image_bytes],
                             stream=True):
        # Print the response to the console and add it to the full response
        print(response['response'], end='', flush=True)
        full_response += response['response']

    df.loc[len(df)] = [image_file, full_response]

for image_file in image_paths:
    if image_file not in df['image_file'].values:
        process_image(image_file)

# Save the DataFrame to a CSV file
df.to_csv('image_descriptions.csv', index=False)