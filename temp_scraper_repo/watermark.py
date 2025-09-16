"""
Watermark Overlay Module - Fixed for Alpine Linux compatibility
Handles watermark generation and application for trial users
"""

from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


class WatermarkOverlay:
    """Class for handling watermark overlays on images"""

    def __init__(self, app_name="MediaScraper"):
        self.app_name = app_name
        self.watermark_text = f"Subscribe for Full Access - {app_name}"
        self.font_size = 48
        self.opacity = 0.3

    def create_text_watermark(self, size):
        """Create a text-based watermark"""
        width, height = size

        # Create transparent overlay
        watermark = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        # Try to load a font
        try:
            # Try to use a truetype font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", self.font_size)
        except:
            try:
                # Fallback to default font
                font = ImageFont.load_default()
            except:
                font = None

        text = self.watermark_text

        # Get text dimensions
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(text) * 10
            text_height = 20

        # Create diagonal pattern
        spacing = max(text_width, text_height) + 50
        positions = []

        # Calculate starting positions
        start_x = -text_width
        start_y = height

        while start_x < width or start_y > -text_height:
            positions.append((start_x, start_y))
            start_x += spacing
            start_y -= spacing

        # Draw watermarks
        for x, y in positions:
            if font:
                draw.text((x, y), text, fill=(255, 255, 255, int(255 * self.opacity)),
                         font=font, stroke_width=2, stroke_fill=(0, 0, 0, int(255 * self.opacity)))
            else:
                draw.text((x, y), text, fill=(255, 255, 255, int(255 * self.opacity)))

        # Rotate the entire watermark image
        watermark = watermark.rotate(45, expand=1)

        # Crop to original size
        new_width, new_height = watermark.size
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        right = left + width
        bottom = top + height
        watermark = watermark.crop((left, top, right, bottom))

        return watermark

    def apply_watermark_to_image(self, image_path, output_path=None):
        """Apply watermark to an image file"""
        try:
            # Open the image
            img = Image.open(image_path)

            # Convert to RGBA if necessary
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create watermark
            watermark = self.create_text_watermark(img.size)

            # Composite the watermark onto the image
            watermarked = Image.alpha_composite(img, watermark)

            # Convert back to RGB for saving as JPEG
            if output_path and output_path.lower().endswith(('.jpg', '.jpeg')):
                watermarked = watermarked.convert('RGB')

            # Save or return
            if output_path:
                watermarked.save(output_path)
                return output_path
            else:
                return watermarked

        except Exception as e:
            print(f"Error applying watermark to image: {e}")
            return None

    def apply_watermark_to_image_bytes(self, image_bytes):
        """Apply watermark to image bytes and return watermarked bytes"""
        try:
            # Open image from bytes
            img = Image.open(BytesIO(image_bytes))

            # Convert to RGBA if necessary
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create watermark
            watermark = self.create_text_watermark(img.size)

            # Composite the watermark onto the image
            watermarked = Image.alpha_composite(img, watermark)

            # Convert back to RGB
            watermarked = watermarked.convert('RGB')

            # Save to bytes
            output = BytesIO()
            watermarked.save(output, format='JPEG', quality=90)
            output.seek(0)

            return output.getvalue()

        except Exception as e:
            print(f"Error applying watermark to image bytes: {e}")
            return image_bytes

    def apply_watermark_to_video(self, video_path, output_path=None):
        """Apply watermark to a video file - OpenCV disabled for compatibility"""
        try:
            # OpenCV functionality disabled for Alpine Linux compatibility
            print(f"Video watermarking disabled - OpenCV not available")
            print(f"Would watermark video: {video_path}")
            if output_path:
                # Just copy the original file
                import shutil
                shutil.copy2(video_path, output_path)
                return output_path
            return None

        except Exception as e:
            print(f"Error in video watermark function: {str(e)}")
            return None

# Global watermark instance
watermark_overlay = WatermarkOverlay()

def get_watermark_css():
    """Return CSS for watermark styling"""
    return """
    .watermarked-media {
        position: relative;
    }

    .watermarked-media::before {
        content: 'Subscribe for Full Access';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(45deg);
        color: rgba(255, 255, 255, 0.3);
        font-size: 24px;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        pointer-events: none;
        z-index: 10;
    }
    """

def get_watermark_html():
    """Return HTML for watermark overlay"""
    return """
    <div class="watermark-overlay" style="
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 100px,
            rgba(255, 255, 255, 0.1) 100px,
            rgba(255, 255, 255, 0.1) 120px
        );
        pointer-events: none;
        z-index: 10;
    ">
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(45deg);
            color: rgba(255, 255, 255, 0.3);
            font-size: 24px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        ">Subscribe for Full Access</div>
    </div>
    """
