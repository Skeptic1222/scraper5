"""
Watermark Overlay Module
Handles watermark generation and application for trial users
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cv2
import numpy as np
from io import BytesIO
import base64

class WatermarkOverlay:
    """Class for handling watermark overlays on images and videos"""
    
    def __init__(self, app_name="MediaScraper"):
        self.app_name = app_name
        self.watermark_text = f"Subscribe for Full Access - {app_name}"
        self.font_size = 48
        self.opacity = 0.3
        
    def create_text_watermark(self, size, text=None):
        """Create a diagonal text watermark as PIL Image"""
        if text is None:
            text = self.watermark_text
            
        # Create transparent image
        watermark = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text dimensions
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate diagonal position (bottom-left to top-right)
        width, height = size
        
        # Create multiple watermarks across the image
        positions = []
        spacing = 300  # Spacing between watermarks
        
        # Calculate starting position for diagonal pattern
        start_x = -text_width
        start_y = height
        
        while start_x < width or start_y > -text_height:
            positions.append((start_x, start_y))
            start_x += spacing
            start_y -= spacing
        
        # Draw watermarks
        for x, y in positions:
            draw.text((x, y), text, fill=(255, 255, 255, int(255 * self.opacity)), 
                     font=font, stroke_width=2, stroke_fill=(0, 0, 0, int(255 * self.opacity)))
        
        # Rotate the entire watermark image
        watermark = watermark.rotate(45, expand=1)
        
        # Crop to original size
        # Calculate the center crop
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
    
    def create_video_watermark(self, frame_size):
        """Create a watermark for video frames"""
        # Create watermark image
        watermark_img = self.create_text_watermark(frame_size)
        
        # Convert PIL image to numpy array
        watermark_np = np.array(watermark_img)
        
        # Extract alpha channel
        if watermark_np.shape[2] == 4:
            alpha = watermark_np[:, :, 3] / 255.0
            watermark_rgb = watermark_np[:, :, :3]
        else:
            alpha = np.ones((watermark_np.shape[0], watermark_np.shape[1]))
            watermark_rgb = watermark_np
        
        return watermark_rgb, alpha
    
    def apply_watermark_to_video(self, video_path, output_path):
        """Apply watermark to a video file"""
        try:
            # Open video
            cap = cv2.VideoCapture(video_path)
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Create watermark for this video size
            watermark_rgb, alpha = self.create_video_watermark((width, height))
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply watermark using alpha blending
                for c in range(3):
                    frame[:, :, c] = frame[:, :, c] * (1 - alpha) + watermark_rgb[:, :, c] * alpha
                
                # Write frame
                out.write(frame.astype(np.uint8))
            
            # Release everything
            cap.release()
            out.release()
            cv2.destroyAllWindows()
            
            return output_path
            
        except Exception as e:
            print(f"Error applying watermark to video: {e}")
            return None
    
    def generate_css_watermark(self):
        """Generate CSS for overlay watermark"""
        return """
        .watermark-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
            overflow: hidden;
        }
        
        .watermark-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 3em;
            font-weight: bold;
            color: rgba(255, 255, 255, 0.3);
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            white-space: nowrap;
            user-select: none;
        }
        
        .watermark-pattern {
            position: absolute;
            width: 200%;
            height: 200%;
            top: -50%;
            left: -50%;
            background-image: repeating-linear-gradient(
                -45deg,
                transparent,
                transparent 100px,
                rgba(255, 255, 255, 0.1) 100px,
                rgba(255, 255, 255, 0.1) 200px
            );
            transform: rotate(-45deg);
        }
        
        .media-container {
            position: relative;
            display: inline-block;
        }
        
        .media-container.trial-mode img,
        .media-container.trial-mode video {
            filter: brightness(0.9);
        }
        """
    
    def generate_svg_watermark(self, width=800, height=600):
        """Generate SVG watermark"""
        svg = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <pattern id="watermarkPattern" x="0" y="0" width="300" height="300" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">
                    <text x="150" y="150" font-family="Arial, sans-serif" font-size="24" fill="rgba(255,255,255,0.3)" text-anchor="middle" transform="rotate(-45 150 150)">
                        {self.watermark_text}
                    </text>
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#watermarkPattern)" />
        </svg>
        """
        return svg
    
    def generate_html_overlay(self, text=None):
        """Generate HTML for watermark overlay"""
        if text is None:
            text = self.watermark_text
            
        return f"""
        <div class="watermark-overlay">
            <div class="watermark-pattern"></div>
            <div class="watermark-text">{text}</div>
        </div>
        """

# Create a global instance
watermark_overlay = WatermarkOverlay()

# Utility functions
def add_watermark_to_image(image_path, output_path=None):
    """Convenience function to add watermark to an image"""
    return watermark_overlay.apply_watermark_to_image(image_path, output_path)

def add_watermark_to_video(video_path, output_path):
    """Convenience function to add watermark to a video"""
    return watermark_overlay.apply_watermark_to_video(video_path, output_path)

def get_watermark_css():
    """Get CSS for watermark overlay"""
    return watermark_overlay.generate_css_watermark()

def get_watermark_html(text=None):
    """Get HTML for watermark overlay"""
    return watermark_overlay.generate_html_overlay(text) 