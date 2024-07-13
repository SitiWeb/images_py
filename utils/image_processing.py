import os
from wand.image import Image
from wand.color import Color


class ImageProcessor:
    def __init__(
        self, canvas_width=900, canvas_height=900, background_color="transparent"
    ):
        """
        Initialize the ImageProcessor with default values.
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.background_color = background_color

    def set_canvas_size(self, width, height):
        """
        Set the canvas size.
        """
        self.canvas_width = int(width)
        self.canvas_height = int(height)

    def set_background_color(self, color):
        """
        Set the background color.
        """
        self.background_color = Color(color)

    def resize_image(self, image_path, output_path, additional_name=None):
        """
        Resize and process the image.
        """
        # Normalize the paths to ensure consistency
        image_path = os.path.normpath(image_path)
        output_path = os.path.normpath(output_path)
        print(image_path)
        print(output_path)
        with Image(filename=image_path) as img:
            img.transform(resize=f"{self.canvas_width}x{self.canvas_height}>")

            x_offset = int((self.canvas_width - img.width) / 2)
            y_offset = int((self.canvas_height - img.height) / 2)

            with Image(
                width=self.canvas_width,
                height=self.canvas_height,
                background=self.background_color,
            ) as canvas:
                canvas.composite(img, left=x_offset, top=y_offset)
                # Create a new filename
                new_filename = os.path.splitext(
                    os.path.basename(output_path))[0]
                if additional_name:
                    new_filename += " - " + additional_name.strip()
                new_filename += os.path.splitext(output_path)[1]
                # Construct the final output path
                final_output_path = os.path.join(
                    os.path.dirname(output_path), new_filename
                )
                # Save the image to the final output path
                canvas.save(filename=final_output_path)
                print(f"Saved to: {final_output_path}")


# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    processor.set_canvas_size(900, 900)
    processor.set_background_color("white")
    processor.resize_image("input_image.jpg", "output_image.jpg", "example")
