import os
from wand.image import Image
from wand.color import Color

def set_canvas_size(width, height):
    global canvas_width, canvas_height
    canvas_width = int(width)
    canvas_height = int(height)

def resize_image(image_path, output_path, additional_name):

    # Normalize the paths to ensure consistency
    image_path = os.path.normpath(image_path)
    output_path = os.path.normpath(output_path)

    with Image(filename=image_path) as img:
        img.transform(resize=f'{canvas_width}x{canvas_height}>')
        
        x_offset = int((canvas_width - img.width) / 2)
        y_offset = int((canvas_height - img.height) / 2)
        
        with Image(width=canvas_width, height=canvas_height, background=Color('transparent')) as canvas:
            canvas.composite(img, left=x_offset, top=y_offset)
            # Create a new filename
            new_filename = os.path.splitext(os.path.basename(output_path))[0]
            if additional_name:
                new_filename += " - " + additional_name.strip()
            new_filename += os.path.splitext(output_path)[1]
            # Construct the final output path
            final_output_path = os.path.join(os.path.dirname(output_path), new_filename)
            # Save the image to the final output path
            canvas.save(filename=final_output_path)
            print(f"Saved to: {final_output_path}")
set_canvas_size(900, 900)