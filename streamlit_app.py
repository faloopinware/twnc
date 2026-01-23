import streamlit as st
import re
import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Play Formatter",
    page_icon="🎭",
    layout="centered"
)

class PlayFormatter:
    """Main formatter class that handles play parsing and formatting"""
    
    # Common stage direction indicators
    STAGE_DIRECTION_WORDS = {
        'softly', 'loudly', 'yelling', 'yells', 'whispers', 'shouting', 'shouts',
        'laughing', 'laughs', 'smiling', 'smiles', 'crying', 'cries', 'pause', 'beat',
        'pauses', 'enters', 'exits', 'sits', 'stands', 'walks', 'looks', 'runs',
        'turning', 'looking', 'walking', 'sitting', 'standing', 'pointing', 'gesturing',
        'waving', 'nodding', 'shaking', 'grabbing', 'reaching', 'pulling', 'pushing',
        'squints', 'biting', 'checking', 'imitating', 'patting', 'opens', 'closes',
        'drops', 'takes', 'puts', 'gets', 'sets', 'rushes', 'freezes', 'interrupting'
    }
    
    def __init__(self):
        self.character_names = set()
        self.elements = []
    
    def download_google_doc(self, url: str) -> str:
        """Download a Google Doc as .docx and return the file path"""
        import requests
        import re
        
        # Extract document ID from URL
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)'
        ]
        
        doc_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                doc_id = match.group(1)
                break
        
        if not doc_id:
            raise Exception("Invalid Google Doc URL. Please check the link and try again.")
        
        # Create export URL
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=docx"
        
        # Download the file
        try:
            response = requests.get(export_url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(
                "Could not download Google Doc. Make sure:\n"
                "1. The link is correct\n"
                "2. The document is shared with 'Anyone with the link can view'\n"
                f"Error: {str(e)}"
            )
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
        
    def extract_text_from_docx(self, docx_path: str) -> str:
        """Extract plain text from .docx file using pandoc"""
        try:
            result = subprocess.run(
                ['pandoc', docx_path, '-t', 'plain', '--wrap=none'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Could not extract text from file: {e}")
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from .docx file"""
        if file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            raise Exception("Unsupported file format. Please use .docx files")
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract play metadata from the beginning of the text"""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        metadata = {
            'title': '',
            'subtitle': '',
            'author': '',
            'email': '',
            'draft': 'DRAFT ONE',
            'copyright': '© 2025'
        }
        
        # Title is usually the first significant line
        if lines:
            metadata['title'] = lines[0]
        
        # Look for author (usually within first 5 lines)
        for line in lines[1:6]:
            # Author name is typically capitalized words without special formatting
            if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                metadata['author'] = line
                break
        
        # Look for email anywhere in first 50 lines
        for line in lines[:50]:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', line)
            if email_match:
                metadata['email'] = email_match.group()
                break
        
        # Look for subtitle/scene description
        for line in lines[1:5]:
            if re.search(r'(Scene|Act|One)', line, re.IGNORECASE):
                metadata['subtitle'] = line
                break
        
        return metadata
    
    def identify_character_names(self, text: str) -> None:
        """Identify all character names in the play"""
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Character names: ALL CAPS, reasonable length, not common words
            if re.match(r'^[A-Z][A-Z\s\-\']{1,30}$', line):
                # Filter out common scene/action words
                if line not in ['LIGHTS UP', 'BLACKOUT', 'END', 'THE', 'AND', 'OR', 
                                'LIGHTS', 'CURTAIN', 'SCENE', 'ACT', 'FADE']:
                    # Check if it might be a character name (not too long)
                    if len(line.split()) <= 4:  # Character names usually 1-3 words
                        self.character_names.add(line)
    
    def is_stage_direction(self, text: str) -> bool:
        """Check if a line is likely a stage direction"""
        text_lower = text.lower().strip()
        
        # Check for parentheses (definite stage direction)
        if text.startswith('(') and text.endswith(')'):
            return True
        
        # Check for common stage direction words
        first_word = text_lower.split()[0] if text_lower else ''
        if first_word in self.STAGE_DIRECTION_WORDS:
            return True
        
        # Check for action verbs and descriptive phrases
        if re.search(r'\b(enters|exits|sits down|stands up|walks to|looks at|turns to)\b', text_lower):
            return True
        
        return False
    
    def is_action_line(self, text: str) -> bool:
        """Check if a line is an action/description line"""
        # Action lines typically contain character names and action verbs
        if any(char in text for char in self.character_names):
            if re.search(r'\b(looks|sits|stands|walks|enters|exits|turns|grabs|takes|puts)\b', text, re.IGNORECASE):
                return True
        
        # Long descriptive lines
        if len(text.split()) > 10 and not text.isupper():
            return True
        
        return False
    
    def parse_play(self, text: str) -> List[Dict]:
        """Parse play text into structured elements"""
        lines = text.split('\n')
        elements = []
        
        # First pass: identify character names
        self.identify_character_names(text)
        
        # Find where the actual play content starts
        start_idx = 0
        for i, line in enumerate(lines):
            if (line.strip() in self.character_names or 
                re.match(r'^(ACT|SCENE)', line.strip(), re.IGNORECASE)):
                start_idx = max(0, i - 1)
                break
        
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check for scene/act headings
            if re.match(r'^(ACT|SCENE|INT\.|EXT\.)', line, re.IGNORECASE):
                elements.append({'type': 'scene_heading', 'text': line.upper()})
                i += 1
                continue
            
            # Check for "LIGHTS UP" style openings
            if 'LIGHTS UP' in line.upper():
                elements.append({'type': 'action', 'text': line})
                i += 1
                continue
            
            # Check for standalone "Beat."
            if line.strip() in ['Beat.', 'Beat', 'beat.', 'beat']:
                elements.append({'type': 'action', 'text': 'Beat.'})
                i += 1
                continue
            
            # Check if this is a character name
            if line in self.character_names:
                char_name = line
                elements.append({'type': 'character', 'text': char_name})
                
                i += 1
                
                # Collect all dialogue and stage directions for this character
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    if not next_line:
                        i += 1
                        if i < len(lines) and lines[i].strip():
                            if lines[i].strip() in self.character_names:
                                break
                            if self.is_action_line(lines[i].strip()):
                                break
                        continue
                    
                    if next_line in self.character_names:
                        break
                    
                    if re.match(r'^(ACT|SCENE)', next_line, re.IGNORECASE):
                        break
                    
                    # Check if line starts with parenthetical
                    if next_line.startswith('(') and ')' in next_line:
                        paren_end = next_line.find(')')
                        if paren_end < len(next_line) - 1:
                            # Inline parenthetical with dialogue
                            elements.append({'type': 'dialogue', 'text': next_line})
                        else:
                            # Standalone parenthetical
                            dir_text = next_line.strip('()')
                            elements.append({'type': 'stage_direction', 'text': dir_text})
                    elif self.is_stage_direction(next_line) and not ' ' in next_line[:15]:
                        elements.append({'type': 'stage_direction', 'text': next_line})
                    else:
                        elements.append({'type': 'dialogue', 'text': next_line})
                    
                    i += 1
                
                continue
            
            # Action/description lines
            if self.is_action_line(line):
                elements.append({'type': 'action', 'text': line})
            elif line and not line.isupper() and len(line) > 5:
                elements.append({'type': 'action', 'text': line})
            
            i += 1
        
        return elements
    
    def create_formatted_docx(self, elements: List[Dict], metadata: Dict, output_path: str):
        """Create professionally formatted .docx file"""
        
        # Write data to a JSON file that JavaScript can read
        data = {
            'metadata': metadata,
            'elements': elements,
            'outputPath': output_path
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json.dump(data, json_file)
            json_path = json_file.name
        
        # Create JavaScript code that reads from the JSON file
        js_code = f'''
const {{ Document, Packer, Paragraph, TextRun, AlignmentType }} = require('docx');
const fs = require('fs');

// Read data from JSON file
const data = JSON.parse(fs.readFileSync({json.dumps(json_path)}, 'utf8'));
const metadata = data.metadata;
const elements = data.elements;
const outputPath = data.outputPath;

// Create title page
function createTitlePage() {
    return [
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 2880, after: 240 },
            children: [new TextRun({ text: metadata.title || "Untitled Play", bold: true, size: 32, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 480 },
            children: [new TextRun({ text: metadata.subtitle || "A 10-minute Play", size: 24, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 480, after: 120 },
            children: [new TextRun({ text: "By", size: 24, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 480 },
            children: [new TextRun({ text: metadata.author || "Unknown Author", size: 24, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 960 },
            children: [new TextRun({ text: metadata.draft, size: 24, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 120 },
            children: [new TextRun({ text: metadata.email || "", size: 20, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Copyright " + metadata.copyright, size: 20, font: "Times New Roman" })]
        }),
        new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { after: 240 },
            children: [new TextRun({ text: "All rights reserved.", size: 20, font: "Times New Roman" })]
        }),
        new Paragraph({ pageBreakBefore: true, children: [] })
    ];
}

// Create play content
function createPlayContent() {
    const content = [];
    
    for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        
        switch(element.type) {
            case 'scene_heading':
                content.push(new Paragraph({
                    spacing: { before: 480, after: 240 },
                    children: [new TextRun({ 
                        text: element.text, 
                        bold: true, 
                        size: 24, 
                        font: "Times New Roman",
                        allCaps: true
                    })]
                }));
                break;
            
            case 'character':
                content.push(new Paragraph({
                    alignment: AlignmentType.CENTER,
                    spacing: { before: 240, after: 120 },
                    children: [new TextRun({ 
                        text: element.text, 
                        bold: false, 
                        size: 24, 
                        font: "Times New Roman",
                        allCaps: true
                    })]
                }));
                break;
            
            case 'dialogue':
                let dialogueText = element.text;
                let dialogueChildren = [];
                let lastIndex = 0;
                let parenPattern = /\([^)]+\)/g;
                let match;
                
                while ((match = parenPattern.exec(dialogueText)) !== null) {
                    if (match.index > lastIndex) {
                        dialogueChildren.push(new TextRun({ 
                            text: dialogueText.substring(lastIndex, match.index),
                            size: 24,
                            font: "Times New Roman"
                        }));
                    }
                    dialogueChildren.push(new TextRun({ 
                        text: match[0],
                        italics: true,
                        size: 24,
                        font: "Times New Roman"
                    }));
                    lastIndex = match.index + match[0].length;
                }
                
                if (lastIndex < dialogueText.length) {
                    dialogueChildren.push(new TextRun({ 
                        text: dialogueText.substring(lastIndex),
                        size: 24,
                        font: "Times New Roman"
                    }));
                }
                
                if (dialogueChildren.length === 0) {
                    dialogueChildren.push(new TextRun({ 
                        text: dialogueText,
                        size: 24,
                        font: "Times New Roman"
                    }));
                }
                
                content.push(new Paragraph({
                    spacing: { before: 0, after: 120 },
                    indent: { left: 0 },
                    children: dialogueChildren
                }));
                break;
            
            case 'stage_direction':
                let dirText = element.text;
                if (!dirText.startsWith('(')) {
                    dirText = '(' + dirText + ')';
                }
                content.push(new Paragraph({
                    spacing: { before: 0, after: 120 },
                    indent: { left: 1440 },
                    children: [new TextRun({ 
                        text: dirText, 
                        italics: true, 
                        size: 24, 
                        font: "Times New Roman" 
                    })]
                }));
                break;
            
            case 'action':
                content.push(new Paragraph({
                    spacing: { before: 120, after: 120 },
                    indent: { left: 1440 },
                    children: [new TextRun({ 
                        text: element.text, 
                        italics: true, 
                        size: 24, 
                        font: "Times New Roman" 
                    })]
                }));
                break;
        }
    }
    
    return content;
}

const doc = new Document({
    styles: {
        default: {
            document: {
                run: { 
                    font: "Times New Roman", 
                    size: 24 
                }
            }
        }
    },
    sections: [{
        properties: {
            page: {
                size: { 
                    width: 12240,
                    height: 15840
                },
                margin: { 
                    top: 1440,
                    right: 1440, 
                    bottom: 1440, 
                    left: 1440 
                }
            }
        },
        children: [
            ...createTitlePage(),
            ...createPlayContent()
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(outputPath, buffer);
    console.log("Document created successfully");
}).catch(err => {
    console.error("Error creating document:", err);
    process.exit(1);
});
'''
        
        # Write and execute JavaScript
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as js_file:
            js_file.write(js_code)
            js_path = js_file.name
        
        try:
            result = subprocess.run(['node', js_path], check=True, capture_output=True, text=True, timeout=30)
        except subprocess.CalledProcessError as e:
            # Print detailed error
            error_msg = f"Node.js error:\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            raise Exception(f"Could not create formatted document: {error_msg}")
        except subprocess.TimeoutExpired:
            raise Exception("Document creation timed out after 30 seconds")
        finally:
            # Clean up temp files
            try:
                os.unlink(js_path)
                os.unlink(json_path)
            except:
                pass


# Streamlit UI
st.title("🎭 Professional Play Formatter")
st.markdown("### Convert your plays to professional industry-standard formatting")

st.markdown("""
**Supports**: Word documents (.docx) and Google Docs (via link)
""")

st.divider()

# Two input options
st.markdown("### Choose how to upload your play:")

input_method = st.radio(
    "Select input method:",
    ["Upload a file from my computer", "Paste a Google Doc link"],
    label_visibility="collapsed"
)

if input_method == "Upload a file from my computer":
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your play (.docx file)", 
        type=['docx'],
        help="Upload a Microsoft Word document (.docx)"
    )
    gdoc_url = None
else:
    # Google Doc URL input
    uploaded_file = None
    gdoc_url = st.text_input(
        "Paste your Google Doc link here:",
        placeholder="https://docs.google.com/document/d/...",
        help="Make sure your document is shared with 'Anyone with the link can view'"
    )
    
    if gdoc_url:
        st.info("📝 **Important**: Make sure your Google Doc is set to 'Anyone with the link can view'")
        with st.expander("How to share your Google Doc"):
            st.markdown("""
            1. Open your Google Doc
            2. Click the **Share** button (top right)
            3. Click **"Change to anyone with the link"**
            4. Make sure it says **"Anyone with the link"** and **"Viewer"**
            5. Click **Done**
            6. Copy the URL from your browser and paste it above
            """)

if uploaded_file is not None or gdoc_url:
    with st.spinner('Formatting your play...'):
        try:
            # Handle Google Doc URL
            if gdoc_url:
                if not gdoc_url.strip():
                    st.warning("Please paste a Google Doc URL")
                    st.stop()
                
                formatter = PlayFormatter()
                input_path = formatter.download_google_doc(gdoc_url)
                file_name = "Google_Doc"
            # Handle file upload
            else:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                file_name = uploaded_file.name.replace('.docx', '')
                formatter = PlayFormatter()
            
            # Create output path
            output_path = tempfile.mktemp(suffix='_FORMATTED.docx')
            
            # Format the play
            text = formatter.extract_text_from_file(input_path)
            metadata = formatter.extract_metadata(text)
            elements = formatter.parse_play(text)
            formatter.create_formatted_docx(elements, metadata, output_path)
            
            # Clean up input file
            os.unlink(input_path)
            
            # Show success message
            st.success('✅ Play formatted successfully!')
            
            # Show metadata
            with st.expander("📋 Play Information"):
                st.write(f"**Title:** {metadata.get('title', 'Unknown')}")
                st.write(f"**Author:** {metadata.get('author', 'Unknown')}")
                st.write(f"**Characters found:** {len(formatter.character_names)}")
                st.write(f"**Elements processed:** {len(elements)}")
            
            # Download button
            with open(output_path, 'rb') as f:
                formatted_file = f.read()
            
            download_name = f"{file_name}_FORMATTED.docx"
            
            st.download_button(
                label="📥 Download Formatted Play",
                data=formatted_file,
                file_name=download_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
            # Clean up output file
            os.unlink(output_path)
            
        except Exception as e:
            st.error(f"❌ Error formatting play: {str(e)}")
            st.info("Please make sure your file is a valid .docx document with character names in ALL CAPS.")

st.divider()

# Instructions
with st.expander("📖 How to Use"):
    st.markdown("""
    **Option 1: Upload a file**
    1. Click "Upload a file from my computer"
    2. Select your .docx file
    3. Wait for formatting
    4. Download your formatted play
    
    **Option 2: Use a Google Doc link**
    1. Click "Paste a Google Doc link"
    2. Share your Google Doc (set to "Anyone with the link can view")
    3. Copy the URL from your browser
    4. Paste it in the text box
    5. Wait for formatting
    6. Download your formatted play
    
    **Tips for best results:**
    - Character names should be in ALL CAPS in your original file
    - For Google Docs: File → Download → Microsoft Word (.docx) if you prefer to upload directly
    """)

with st.expander("❓ Troubleshooting"):
    st.markdown("""
    **Problem**: "Could not download Google Doc"
    - Make sure the document is shared with "Anyone with the link can view"
    - Check that the URL is complete and correct
    - Try copying the URL again from your browser's address bar
    
    **Problem**: "Error formatting play"
    - Make sure your file is a .docx (not .doc)
    - Check that character names are in ALL CAPS
    
    **Problem**: Character names not detected
    - Make sure they're in ALL CAPS and on their own line
    - The formatter looks for patterns like "KATE" or "TRUDY"
    
    **Problem**: Formatting looks wrong
    - Review the original file for consistency
    - Make sure stage directions are clearly separated from dialogue
    
    **Google Docs tip**: If the link method isn't working, try downloading as .docx and uploading instead
    """)

st.divider()
st.caption("Professional Play Formatter v1.0 | Times New Roman 12pt | Industry Standard Format")
