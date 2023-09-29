import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import os,subprocess,sys,shutil
from PIL import Image,ImageOps

def upscale_image(image_path, output_dir):
    if not image_path.lower().endswith((".png", ".jpeg", ".jpg")):
        print(f"Skipping file {image_path}. Reason: Not a valid image file.")
        return
    try:
        filename, _ = os.path.splitext(os.path.basename(image_path))
        output_file = os.path.join(output_dir, f"{filename}.png")
        print(f"Upscaling image {image_path}...")
        cmd = f"realesrgan-ncnn-vulkan.exe -i {image_path} -o {output_file} -n realesrgan-x4plus"
        process = subprocess.Popen(cmd, shell=True)
        process.wait()
        compress_image(image_path, output_dir, max_size=7, degrade_step=6)
    except Exception as e:
        print(f"Error occured while upscaling the image: {str(e)}")

def compress_image(image_path, output_dir, max_size=4, degrade_step=8):
    filename, _ = os.path.splitext(os.path.basename(image_path))
    output_path = os.path.join(output_dir, f"{filename}.jpg")
    quality = 95 
    try:
        while os.path.getsize(output_path) > max_size * 1024 * 1024:
            if quality <= 20:
                print("Image Compression: Quality <= 20%")
                break
            Image.open(image_path).convert("RGB").save(output_path, "JPEG", quality=quality)
            print(f"Compressed to quality {quality}%")
            if os.path.getsize(output_path) > max_size * 1024 * 1024:
                quality -= degrade_step
            else:
                break
        print("Image Compression Successful!")
    except Exception as e:
        print(f"Error occured while compressing the image: {str(e)}")

def split_image(image_path):
    try:
        image_path=resize_image(image_path)
        img = Image.open(image_path).convert("RGB")

        filename, _ = os.path.splitext(os.path.basename(image_path))
        output_dir = os.path.join(os.path.dirname(image_path), filename)
        os.makedirs(output_dir, exist_ok=True)

        temp_imgs = [os.path.join(output_dir, f"temp_{i}.jpg") for i in range(1,5)]
        upscaled_imgs = [os.path.join(output_dir, f"img{i}.jpg") for i in range(1, 5)]
        
        width, height = img.size

        img.crop((0, 0, width // 2, height // 2)).save(temp_imgs[0])
        img.crop((width // 2, 0, width, height // 2)).save(temp_imgs[1])
        img.crop((0, height // 2, width // 2, height)).save(temp_imgs[2])
        img.crop((width // 2, height // 2, width, height)).save(temp_imgs[3])

        for img in temp_imgs:
            upscale_image(img, output_dir)

        for img in temp_imgs:
            os.remove(img)

        print(f"Process Completed: created {', '.join(upscaled_imgs)}")
    except Exception as e:
        print(f"Error occured while spliting the image: {str(e)}")

def open_dialog_and_choose_file():
    
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def resize_image(image_path):
    try:
        filename, extension = os.path.splitext(image_path)
        new_image_path = f"{filename}_resized{extension}"
        shutil.copy(image_path, new_image_path) 

        img = Image.open(new_image_path) 
        
        # get the size of the image and calculate the new size
        old_size = img.size
        new_size = calculate_new_size(old_size)
        
        img = img.resize(new_size, Image.LANCZOS)
        img = img.convert("RGB")
        img.save(new_image_path)
    except Exception as e:
        print(f"Error occured while resizing the image: {str(e)}")
    return new_image_path

def calculate_new_size(old_size):
    width, height = old_size 
    if width >= 4096 and height >= 4096:
        return (510, 336)
    elif width >= 2000 and height >= 800:
        return (320, 163)
    elif width >= 708 and height >= 536:
        return (255, 163)
    else:
        return (255, 163)


def main(filepath):
    if os.path.isfile(filepath):
        split_image(filepath)
    else:
        print("File not found!")

if __name__ == "__main__":
    if len(sys.argv) > 1: 
        main(sys.argv[1])
    else:
        selected_file = open_dialog_and_choose_file()
        if selected_file:
            main(selected_file)
        else:
            print("No file selected.")
