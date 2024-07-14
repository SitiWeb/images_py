import os
from wand.image import Image
from wand.color import Color


class ImageProcessor:
    def __init__(self, canvas_width=900, canvas_height=900, background_color="transparent", image_size="fit"):
        """
        Initialize the ImageProcessor with default values.
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.background_color = Color(background_color)
        self.image_size = image_size

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

    def set_image_size(self, size):
        """
        Set the image size mode.
        """
        self.image_size = size

    def resize_image(self, image_path, output_path, options):
        """
        Resize and process the image.

        Args:
            image_path (str): The path to the input image.
            output_path (str): The path to the output image.
            additional_name (str, optional): Additional name to append to the output filename.
            mode (str, optional): The resizing mode ("contain", "cover", "fit"). Default is "contain".
        """
        log = options.get("log_message", None)
        
        # Normalize the paths to ensure consistency
        image_path = os.path.normpath(image_path)
        output_path = os.path.normpath(output_path)

        with Image(filename=image_path) as img:
            self.log_message(f"Original image size: {img.width}x{img.height}", log)
            if self.image_size == "contain":
                self._contain(img)
            elif self.image_size == "cover":
                self._cover(img)
            # elif self.image_size == "fit":
            #     self._fit(img)

            x_offset = int((self.canvas_width - img.width) / 2)
            y_offset = int((self.canvas_height - img.height) / 2)

            with Image(width=self.canvas_width, height=self.canvas_height, background=self.background_color) as canvas:
                canvas.composite(img, left=x_offset, top=y_offset)
                # Create a new filename
                new_filename = os.path.splitext(os.path.basename(output_path))[0]

                new_filename += os.path.splitext(output_path)[1]
                # Construct the final output path
                final_output_path = os.path.join(os.path.dirname(output_path), new_filename)
                # Save the image to the final output path
                canvas.save(filename=final_output_path)
                self.log_message(f"Saved to: {final_output_path}", log)


    def _cover(self, img:Image):
        """
        Resize the image to cover the entire canvas.
        """
        base_width = self.canvas_width
        base_heigth = self.canvas_height
        wpercent = (base_width / float(img.size[0]))
        hpercent = (base_heigth / float(img.size[1]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img.resize(wsize, base_heigth)


        aspect_ratio_img = img.width / img.height
        aspect_ratio_canvas = self.canvas_width / self.canvas_height
        print(f"Image aspect ratio: {aspect_ratio_img}, Canvas aspect ratio: {aspect_ratio_canvas}")
        print(f"Cover resized image size: {img.width}x{img.height}")


    def _contain(self, img):
        """
        Resize the image to cover the entire canvas.
        """
        aspect_ratio_img = img.width / img.height
        aspect_ratio_canvas = self.canvas_width / self.canvas_height
        print(f"Image aspect ratio: {aspect_ratio_img}, Canvas aspect ratio: {aspect_ratio_canvas}")

        if aspect_ratio_img > aspect_ratio_canvas:
            img.transform(resize=f"{self.canvas_width}x")
        else:
            img.transform(resize=f"x{self.canvas_height}")
        print(f"Cover resized image size: {img.width}x{img.height}")

    # def _fit(self, img):
    #     """
    #     Fit the image within the canvas without scaling up if it's smaller.
    #     """
    #     if img.width > self.canvas_width or img.height > self.canvas_height:
    #         img.transform(resize=f"{self.canvas_width}x{self.canvas_height}>")
    #     print(f"Fit resized image size: {img.width}x{img.height}")

    def log_message(self, message, log=None):
        """
        Log a message or print it if no log function is provided.

        Args:
            message (str): The message to log or print.
            log (function, optional): The log function to use. Defaults to None.
        """
        if log:
            log(message)
        else:
            print(message)


# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    processor.set_canvas_size(900, 900)
    processor.set_background_color("white")

    # Contain mode
    processor.set_image_size("contain")
    processor.resize_image("input_image.jpg", "output_image_contain.jpg", "example")

    # Cover mode
    processor.set_image_size("cover")
    processor.resize_image("input_image.jpg", "output_image_cover.jpg", "example")

    # Fit mode
    processor.set_image_size("fit")
    processor.resize_image("input_image.jpg", "output_image_fit.jpg", "example")
