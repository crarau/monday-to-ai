#!/usr/bin/env python3
"""
Monday.com Task Exporter - Creates a complete readable export of Monday.com items
Generates markdown with embedded images and optional PDF export
"""

import requests
import json
import os
import re
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import sys

class MondayExporter:
    """Export Monday.com items to readable formats (Markdown/PDF)"""
    
    API_URL = "https://api.monday.com/v2"
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json",
            "API-Version": "2024-01"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute GraphQL query"""
        payload = {"query": query, "variables": variables or {}}
        
        response = self.session.post(self.API_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        
        result = response.json()
        if "errors" in result:
            raise Exception(f"GraphQL errors: {result['errors']}")
        
        return result
    
    def get_item_complete(self, item_id: str) -> Dict[str, Any]:
        """Get complete item data including all content"""
        query = """
        query ($itemId: ID!) {
            items(ids: [$itemId]) {
                id
                name
                state
                created_at
                updated_at
                creator {
                    id
                    name
                    email
                }
                board {
                    id
                    name
                    workspace {
                        name
                    }
                }
                group {
                    title
                    color
                }
                column_values {
                    id
                    type
                    text
                    value
                }
                assets {
                    id
                    name
                    url
                    public_url
                    file_extension
                    file_size
                }
                updates(limit: 100) {
                    id
                    body
                    text_body
                    created_at
                    creator {
                        name
                    }
                    assets {
                        id
                        name
                        url
                        public_url
                        file_extension
                    }
                    replies {
                        id
                        body
                        text_body
                        created_at
                        creator {
                            name
                        }
                    }
                }
            }
        }
        """
        
        result = self.execute_query(query, {"itemId": item_id})
        
        if not result.get("data", {}).get("items"):
            raise Exception(f"No item found with ID: {item_id}")
        
        return result["data"]["items"][0]
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename[:200].strip()
    
    def download_image(self, url: str, filepath: Path) -> bool:
        """Download image file"""
        try:
            # Handle pre-signed S3 URLs
            if "s3.amazonaws.com" in url or "X-Amz-Algorithm" in url:
                response = requests.get(url, timeout=60)
            else:
                response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_bytes(response.content)
                return True
        except:
            pass
        return False
    
    def extract_images_from_html(self, html: str) -> List[str]:
        """Extract image URLs from HTML content"""
        urls = []
        patterns = [
            r'<img[^>]*src="([^"]+)"[^>]*>',
            r'!\[.*?\]\((https?://[^\)]+)\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            urls.extend(matches)
        
        return list(set(urls))
    
    def get_asset_public_url(self, asset_id: str) -> Optional[str]:
        """Get public URL for an asset"""
        query = """
        query ($assetId: ID!) {
            assets(ids: [$assetId]) {
                public_url
                url
            }
        }
        """
        
        try:
            result = self.execute_query(query, {"assetId": asset_id})
            if result.get("data", {}).get("assets"):
                asset = result["data"]["assets"][0]
                return asset.get("public_url") or asset.get("url")
        except:
            pass
        return None
    
    def export_to_markdown(self, item_id: str, output_dir: Path = None) -> Path:
        """Export Monday.com item to a comprehensive markdown file with images"""
        
        # Get item data
        print(f"📋 Fetching item {item_id}...")
        item = self.get_item_complete(item_id)
        
        # Create output directory based on task name
        task_name = self.sanitize_filename(item.get("name", f"task_{item_id}"))
        if output_dir is None:
            output_dir = Path.cwd() / task_name
        else:
            output_dir = output_dir / task_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        print(f"📁 Creating export in: {output_dir}")
        
        # Start building markdown content
        md_content = []
        
        # Header
        md_content.append(f"# {item.get('name', 'Untitled Task')}\n")
        md_content.append(f"*Exported from Monday.com on {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
        md_content.append("---\n")
        
        # Metadata section
        md_content.append("## 📌 Task Information\n")
        md_content.append(f"- **Board:** {item.get('board', {}).get('name')}")
        md_content.append(f"- **Workspace:** {item.get('board', {}).get('workspace', {}).get('name')}")
        md_content.append(f"- **Group:** {item.get('group', {}).get('title')}")
        md_content.append(f"- **Status:** {item.get('state')}")
        md_content.append(f"- **Created:** {item.get('created_at')}")
        md_content.append(f"- **Updated:** {item.get('updated_at')}")
        md_content.append(f"- **Creator:** {item.get('creator', {}).get('name')} ({item.get('creator', {}).get('email')})")
        md_content.append("\n")
        
        # Column values
        columns = item.get("column_values", [])
        if columns:
            md_content.append("## 📊 Fields\n")
            for col in columns:
                if col.get("text"):
                    col_type = col.get("type", "text")
                    if col_type == "people":
                        md_content.append(f"- **Assigned to:** {col.get('text')}")
                    elif col_type == "status":
                        md_content.append(f"- **Status:** {col.get('text')}")
                    elif col_type == "date":
                        md_content.append(f"- **Date:** {col.get('text')}")
                    else:
                        md_content.append(f"- **{col_type.title()}:** {col.get('text')}")
            md_content.append("\n")
        
        # Download and reference direct assets
        assets = item.get("assets", [])
        if assets:
            md_content.append("## 📎 Attachments\n")
            for i, asset in enumerate(assets):
                name = asset.get("name", f"attachment_{i}")
                url = asset.get("public_url") or asset.get("url")
                
                if url:
                    file_path = images_dir / self.sanitize_filename(name)
                    if self.download_image(url, file_path):
                        rel_path = f"images/{file_path.name}"
                        
                        # Check if it's an image
                        if any(ext in name.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
                            md_content.append(f"![{name}]({rel_path})")
                        else:
                            md_content.append(f"- [{name}]({rel_path})")
                        
                        print(f"  ✓ Downloaded: {name}")
            md_content.append("\n")
        
        # Updates/Comments section
        updates = item.get("updates", [])
        if updates:
            md_content.append("## 💬 Comments & Updates\n")
            
            for update_idx, update in enumerate(updates):
                creator = update.get("creator", {}).get("name", "Unknown")
                created = update.get("created_at", "")
                body = update.get("body", "")
                text_body = update.get("text_body", "")
                
                # Format date
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        created = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                md_content.append(f"### 💭 {creator} - {created}\n")
                
                # Process HTML body for images
                if body:
                    # Extract and download images from HTML
                    img_urls = self.extract_images_from_html(body)
                    
                    for img_idx, img_url in enumerate(img_urls):
                        # Try to get asset ID from URL
                        asset_match = re.search(r'/resources/(\d+)/', img_url)
                        if asset_match:
                            asset_id = asset_match.group(1)
                            public_url = self.get_asset_public_url(asset_id)
                            if public_url:
                                img_url = public_url
                        
                        filename = f"comment_{update_idx}_{img_idx}.png"
                        file_path = images_dir / filename
                        
                        if self.download_image(img_url, file_path):
                            rel_path = f"images/{filename}"
                            # Replace image in text with markdown image
                            text_body += f"\n\n![Image]({rel_path})"
                            print(f"  ✓ Downloaded comment image: {filename}")
                
                # Add the text content
                if text_body:
                    # Clean up the text
                    text_body = text_body.strip()
                    md_content.append(text_body)
                    md_content.append("\n")
                
                # Process update assets
                update_assets = update.get("assets", [])
                if update_assets:
                    for asset in update_assets:
                        name = asset.get("name", "file")
                        url = asset.get("public_url") or asset.get("url")
                        
                        if url:
                            file_path = images_dir / f"update_{update_idx}_{self.sanitize_filename(name)}"
                            if self.download_image(url, file_path):
                                rel_path = f"images/{file_path.name}"
                                
                                if any(ext in name.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                                    md_content.append(f"\n![{name}]({rel_path})\n")
                                else:
                                    md_content.append(f"\nAttachment: [{name}]({rel_path})\n")
                                
                                print(f"  ✓ Downloaded update attachment: {name}")
                
                # Process replies
                replies = update.get("replies", [])
                if replies:
                    md_content.append("\n#### 💬 Replies:\n")
                    
                    for reply_idx, reply in enumerate(replies):
                        reply_creator = reply.get("creator", {}).get("name", "Unknown")
                        reply_text = reply.get("text_body", "")
                        reply_body = reply.get("body", "")
                        reply_created = reply.get("created_at", "")
                        
                        # Format date
                        if reply_created:
                            try:
                                dt = datetime.fromisoformat(reply_created.replace("Z", "+00:00"))
                                reply_created = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        
                        md_content.append(f"\n**↳ {reply_creator}** - {reply_created}\n")
                        
                        # Process HTML body for images in replies
                        if reply_body:
                            # Extract and download images from reply HTML
                            reply_img_urls = self.extract_images_from_html(reply_body)
                            
                            for img_idx, img_url in enumerate(reply_img_urls):
                                # Try to get asset ID from URL
                                asset_match = re.search(r'/resources/(\d+)/', img_url)
                                if asset_match:
                                    asset_id = asset_match.group(1)
                                    public_url = self.get_asset_public_url(asset_id)
                                    if public_url:
                                        img_url = public_url
                                
                                filename = f"reply_{update_idx}_{reply_idx}_{img_idx}.png"
                                file_path = images_dir / filename
                                
                                if self.download_image(img_url, file_path):
                                    rel_path = f"images/{filename}"
                                    # Add image to reply text
                                    reply_text += f"\n\n![Image]({rel_path})"
                                    print(f"  ✓ Downloaded reply image: {filename}")
                        
                        # Add the reply text content
                        if reply_text:
                            # Indent reply text
                            reply_lines = reply_text.strip().split('\n')
                            for line in reply_lines:
                                if line.strip():
                                    md_content.append(f"  {line}")
                            md_content.append("")
                
                md_content.append("---\n")
        
        # Write markdown file - always named README.md for consistency
        md_file = output_dir / "README.md"
        md_file.write_text("\n".join(md_content), encoding="utf-8")
        
        print(f"\n✅ Export complete!")
        print(f"📄 Markdown file: {md_file}")
        print(f"🖼️  Images folder: {images_dir}")
        
        # Don't create metadata file - keep structure minimal
        
        return md_file
    
    def export_to_pdf(self, markdown_file: Path) -> Optional[Path]:
        """Convert markdown to PDF (requires markdown-pdf or pandoc)"""
        try:
            import subprocess
            
            pdf_file = markdown_file.with_suffix('.pdf')
            
            # Try pandoc first (better formatting)
            try:
                subprocess.run([
                    "pandoc",
                    str(markdown_file),
                    "-o", str(pdf_file),
                    "--pdf-engine=xelatex",
                    "-V", "geometry:margin=1in",
                    "-V", "linkcolor=blue",
                    "-V", "urlcolor=blue"
                ], check=True, capture_output=True)
                
                print(f"📑 PDF created: {pdf_file}")
                return pdf_file
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try wkhtmltopdf as fallback
                try:
                    # First convert markdown to HTML
                    html_content = f"""
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                            img {{ max-width: 100%; height: auto; }}
                            pre {{ background: #f4f4f4; padding: 10px; overflow-x: auto; }}
                            code {{ background: #f4f4f4; padding: 2px 4px; }}
                        </style>
                    </head>
                    <body>
                    """
                    
                    # Simple markdown to HTML conversion
                    md_content = markdown_file.read_text()
                    # This is very basic - for production use a proper markdown parser
                    md_content = md_content.replace("# ", "<h1>").replace("\n## ", "</h1>\n<h2>")
                    md_content = md_content.replace("\n### ", "</h2>\n<h3>").replace("\n", "<br>\n")
                    
                    html_content += md_content + "</body></html>"
                    
                    html_file = markdown_file.with_suffix('.html')
                    html_file.write_text(html_content)
                    
                    subprocess.run([
                        "wkhtmltopdf",
                        str(html_file),
                        str(pdf_file)
                    ], check=True, capture_output=True)
                    
                    html_file.unlink()  # Clean up temp HTML
                    print(f"📑 PDF created: {pdf_file}")
                    return pdf_file
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("⚠️  PDF generation requires pandoc or wkhtmltopdf")
                    print("   Install with: apt-get install pandoc or apt-get install wkhtmltopdf")
                    
        except ImportError:
            print("⚠️  PDF generation not available")
        
        return None


def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip()


def parse_monday_url(url: str) -> str:
    """Extract item ID from Monday.com URL"""
    parts = url.split("/")
    for i, part in enumerate(parts):
        if part == "pulses" and i + 1 < len(parts):
            return parts[i + 1]
    return url  # Return as-is if not a URL


def main():
    """Main entry point"""
    
    print("📚 Monday.com Task Exporter")
    print("=" * 60)
    
    # Load .env file
    load_env()
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python monday_exporter.py <url_or_item_id> [--pdf]")
        print("\nExamples:")
        print("  python monday_exporter.py https://example.monday.com/boards/123/pulses/456")
        print("  python monday_exporter.py 456")
        print("  python monday_exporter.py 456 --pdf")
        return 1
    
    # Get item ID
    input_arg = sys.argv[1]
    item_id = parse_monday_url(input_arg)
    generate_pdf = "--pdf" in sys.argv
    
    print(f"📍 Item ID: {item_id}")
    
    # Get API token
    api_token = os.getenv("MONDAY_API_TOKEN")
    if not api_token:
        print("\n❌ No Monday.com API token found!")
        print("   Please create a .env file with your Monday.com API token:")
        print("   echo 'MONDAY_API_TOKEN=your-token-here' > .env")
        print("\n   To get your token:")
        print("   1. Go to monday.com")
        print("   2. Click your avatar → Developers")
        print("   3. Create a personal API token")
        return 1
    else:
        print("✓ Using API token from .env file")
    
    try:
        exporter = MondayExporter(api_token)
        
        # Export to markdown
        md_file = exporter.export_to_markdown(item_id)
        
        # Generate PDF if requested
        if generate_pdf:
            pdf_file = exporter.export_to_pdf(md_file)
            if pdf_file:
                print(f"\n📚 Complete export available at:")
                print(f"   - Markdown: {md_file}")
                print(f"   - PDF: {pdf_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())