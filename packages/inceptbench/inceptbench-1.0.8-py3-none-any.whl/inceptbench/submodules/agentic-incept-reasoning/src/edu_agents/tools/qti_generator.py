import os
import re
import uuid
import zipfile
import tempfile
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Callable, List, Optional
import logging
from edu_agents.core.api_key_manager import get_async_openai_client
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class QTIGenerator:
    """Generates QTI-formatted assessment content from markdown input."""
    
    def __init__(self):
        self.client = get_async_openai_client(timeout=180.0)
        
    async def generate_qti_package(self, markdown_content: str) -> str:
        """
        Generate a complete QTI package from markdown content.
        
        Parameters
        ----------
        markdown_content : str
            Markdown formatted question(s) content
            
        Returns
        -------
        str
            Path to the generated QTI package zip file
        """
        try:
            # Extract images from markdown
            images = self._extract_images(markdown_content)
            
            # Download images to temporary directory
            temp_dir = tempfile.mkdtemp()
            downloaded_images = {}
            
            for img_url, img_alt in images:
                try:
                    local_path = self._download_image(img_url, temp_dir)
                    downloaded_images[img_url] = {
                        'local_path': local_path,
                        'filename': os.path.basename(local_path),
                        'alt_text': img_alt
                    }
                except Exception as e:
                    logger.warning(f"Failed to download image {img_url}: {e}")
            
            # Generate QTI XML using GPT-4o
            qti_xml = await self._generate_qti_xml(markdown_content, downloaded_images)
            
            # Create QTI package
            package_path = self._create_qti_package(qti_xml, downloaded_images, temp_dir)
            
            return package_path
            
        except Exception as e:
            error_message = f"Error generating QTI package: {str(e)}"
            logger.error(error_message)
            raise RuntimeError(error_message)
    
    def _extract_images(self, markdown_content: str) -> List[tuple]:
        """Extract image URLs and alt text from markdown."""
        # Pattern to match markdown images: ![alt text](url)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, markdown_content)
        return [(url.split('?')[0], alt) for alt, url in matches]  # Remove query params
    
    def _download_image(self, url: str, temp_dir: str) -> str:
        """Download an image to the temporary directory."""
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Generate filename from URL or use UUID
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            # Get extension from content-type if available
            content_type = response.headers.get('content-type', '')
            if 'png' in content_type:
                filename = f"{uuid.uuid4().hex}.png"
            elif 'jpeg' in content_type or 'jpg' in content_type:
                filename = f"{uuid.uuid4().hex}.jpg"
            else:
                filename = f"{uuid.uuid4().hex}.png"  # Default to PNG
        
        local_path = os.path.join(temp_dir, filename)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        return local_path
    
    async def _generate_qti_xml(self, markdown_content: str, downloaded_images: Dict) -> str:
        """Use GPT-4o to generate QTI XML from markdown content."""
        
        # Create image reference mapping for the prompt
        image_refs = {}
        for orig_url, img_data in downloaded_images.items():
            image_refs[orig_url] = img_data['filename']
        
        system_prompt = """You are an expert in QTI (Question & Test Interoperability) 3.0 specification. Your task is to convert markdown-formatted assessment content into valid QTI 3.0 XML.

Key requirements:
1. Generate complete, valid QTI 3.0 XML that follows the specification
2. Support multiple interaction types (choiceInteraction, extendedTextInteraction, etc.)
3. Include proper response processing for scoring
4. Handle images by referencing the provided local filenames
5. Create outcome declarations for scoring
6. Generate appropriate feedback based on the content
7. Use proper QTI namespaces and structure
8. DO NOT place the XML in a code block. Return only the XML.

For the example provided, create:
- A choiceInteraction for multiple choice questions
- An extendedTextInteraction for explanation/reasoning questions
- Response processing that scores both parts
- Outcome declarations for partial and total scores
- Appropriate identifiers and structure

Return only the complete QTI XML without additional explanation."""

        user_prompt = f"""Convert this markdown assessment content to QTI 3.0 XML:

{markdown_content}

Available image files (use these filenames in your XML):
{image_refs}

Generate complete QTI XML with proper structure, interactions, response processing, and scoring."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                max_tokens=4000
            )
            
            # Defensive check: ensure content is not a coroutine
            response_content = response.choices[0].message.content
            if hasattr(response_content, '__await__'):
                response_content = await response_content
            response_text = response_content.strip()
            response_text = response_text.replace("```xml", "").replace("```", "")
            return response_text
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate QTI XML: {str(e)}")
    
    def _create_qti_package(self, qti_xml: str, downloaded_images: Dict, temp_dir: str) -> str:
        """Create a complete QTI package with manifest."""
        
        # Create package directory structure
        package_dir = os.path.join(temp_dir, 'qti_package')
        os.makedirs(package_dir, exist_ok=True)
        
        # Write QTI XML file
        item_filename = f"item_{uuid.uuid4().hex[:8]}.xml"
        item_path = os.path.join(package_dir, item_filename)
        with open(item_path, 'w', encoding='utf-8') as f:
            f.write(qti_xml)
        
        # Copy images to package
        image_files = []
        for orig_url, img_data in downloaded_images.items():
            dest_path = os.path.join(package_dir, img_data['filename'])
            with open(img_data['local_path'], 'rb') as src:
                with open(dest_path, 'wb') as dst:
                    dst.write(src.read())
            image_files.append(img_data['filename'])
        
        # Create manifest
        manifest_xml = self._create_manifest(item_filename, image_files)
        manifest_path = os.path.join(package_dir, 'imsmanifest.xml')
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_xml)
        
        # Create ZIP package
        package_zip_path = os.path.join(temp_dir, f"qti_package_{uuid.uuid4().hex[:8]}.zip")
        with zipfile.ZipFile(package_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arc_name)
        
        return package_zip_path
    
    def _create_manifest(self, item_filename: str, image_files: List[str]) -> str:
        """Create IMS Content Packaging manifest."""
        
        manifest_template = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          identifier="MANIFEST_{uuid.uuid4().hex[:8]}"
          version="1.0"
          xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 
                              http://www.imsglobal.org/xsd/qti/qtiv3p0/imscp_v1p1.xsd">
    
    <metadata>
        <lom xmlns="http://ltsc.ieee.org/xsd/LOM">
            <general>
                <title>
                    <string language="en">QTI Assessment Item</string>
                </title>
                <description>
                    <string language="en">Generated QTI 3.0 Assessment Item</string>
                </description>
            </general>
        </lom>
    </metadata>
    
    <organizations/>
    
    <resources>
        <resource identifier="ITEM_{uuid.uuid4().hex[:8]}" 
                  type="imsqti_item_xmlv3p0" 
                  href="{item_filename}">
            <file href="{item_filename}"/>
            {self._generate_image_file_entries(image_files)}
        </resource>
    </resources>
</manifest>"""
        
        return manifest_template
    
    def _generate_image_file_entries(self, image_files: List[str]) -> str:
        """Generate file entries for images in the manifest."""
        entries = []
        for image_file in image_files:
            entries.append(f'            <file href="{image_file}"/>')
        return '\n'.join(entries)


def generate_qti_tool() -> tuple[Dict[str, Any], Callable]:
    """Generate the QTI conversion tool specification and function."""
    
    generator = QTIGenerator()
    
    async def qti_conversion_function(markdown_content: str) -> str:
        """Convert markdown content to QTI package."""
        return await generator.generate_qti_package(markdown_content)
    
    spec = {
        "type": "function",
        "name": "convert_to_qti",
        "description": "Convert markdown-formatted assessment content to QTI 3.0 format. Creates a complete QTI package with manifest and downloads any referenced images.",
        "parameters": {
            "type": "object",
            "properties": {
                "markdown_content": {
                    "type": "string",
                    "description": "Markdown formatted assessment content containing questions, answers, and metadata. Can include single questions or multiple questions."
                }
            },
            "required": ["markdown_content"]
        }
    }
    
    return spec, qti_conversion_function 