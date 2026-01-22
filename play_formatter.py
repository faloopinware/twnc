#!/usr/bin/env python3
"""
Professional Play Formatter
Converts inconsistently formatted plays to industry-standard screenplay format
Handles Word documents (.docx) and Google Docs exports
"""

import re
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional

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
            print(f"Error: Could not extract text from {docx_path}")
            print("Make sure the file is a valid .docx file")
            sys.exit(1)
    
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
        
        # Find where the actual play content starts (after title, author, etc.)
        start_idx = 0
        for i, line in enumerate(lines):
            # Look for first character name or "ACT" or "SCENE"
            if (line.strip() in self.character_names or 
                re.match(r'^(ACT|SCENE)', line.strip(), re.IGNORECASE)):
                start_idx = max(0, i - 1)  # Include one line before for context
                break
        
        i = start_idx
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check for scene/act headings
            if re.match(r'^(ACT|SCENE|INT\.|EXT\.)', line, re.IGNORECASE):
                elements.append({
                    'type': 'scene_heading',
                    'text': line.upper()
                })
                i += 1
                continue
            
            # Check for "LIGHTS UP" style openings
            if 'LIGHTS UP' in line.upper():
                elements.append({
                    'type': 'action',
                    'text': line
                })
                i += 1
                continue
            
            # Check for standalone "Beat."
            if line.strip() in ['Beat.', 'Beat', 'beat.', 'beat']:
                elements.append({
                    'type': 'action',
                    'text': 'Beat.'
                })
                i += 1
                continue
            
            # Check if this is a character name
            if line in self.character_names:
                char_name = line
                elements.append({
                    'type': 'character',
                    'text': char_name
                })
                
                i += 1
                
                # Collect all dialogue and stage directions for this character
                while i < len(lines):
                    next_line = lines[i].strip()
                    
                    # Empty line - might be end of this character's speech
                    if not next_line:
                        i += 1
                        # Check if there's more after the empty line
                        if i < len(lines) and lines[i].strip():
                            # If next non-empty line is another character, we're done
                            if lines[i].strip() in self.character_names:
                                break
                            # If it's an action line (character doing something), we're done
                            if self.is_action_line(lines[i].strip()):
                                break
                        continue
                    
                    # Next character name - end of current character's speech
                    if next_line in self.character_names:
                        break
                    
                    # Scene heading - end of speech
                    if re.match(r'^(ACT|SCENE)', next_line, re.IGNORECASE):
                        break
                    
                    # Check if line starts with parenthetical (stage direction on own line)
                    if next_line.startswith('(') and ')' in next_line:
                        # Check if there's dialogue after the parenthetical on same line
                        paren_end = next_line.find(')')
                        if paren_end < len(next_line) - 1:
                            # Inline parenthetical with dialogue
                            elements.append({
                                'type': 'dialogue',
                                'text': next_line
                            })
                        else:
                            # Standalone parenthetical
                            dir_text = next_line.strip('()')
                            elements.append({
                                'type': 'stage_direction',
                                'text': dir_text
                            })
                    # Stage direction word at start of line (like "softly", "yelling")
                    elif self.is_stage_direction(next_line) and not ' ' in next_line[:15]:
                        # Single word stage direction
                        elements.append({
                            'type': 'stage_direction',
                            'text': next_line
                        })
                    # Regular dialogue
                    else:
                        elements.append({
                            'type': 'dialogue',
                            'text': next_line
                        })
                    
                    i += 1
                
                continue
            
            # Action/description lines (character doing something)
            if self.is_action_line(line):
                elements.append({
                    'type': 'action',
                    'text': line
                })
            # Default to action if we can't categorize it
            elif line and not line.isupper() and len(line) > 5:
                elements.append({
                    'type': 'action',
                    'text': line
                })
            
            i += 1
        
        return elements
    
    def create_formatted_docx(self, elements: List[Dict], metadata: Dict, output_path: str):
        """Create professionally formatted .docx file"""
        
        # Create JavaScript code for docx generation
        js_code = '''
const { Document, Packer, Paragraph, TextRun, AlignmentType, PageBreak } = require('docx');
const fs = require('fs');

const metadata = ''' + json.dumps(metadata) + ''';
const elements = ''' + json.dumps(elements) + ''';

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

// Create play content with proper formatting
function createPlayContent() {
    const content = [];
    let pageNumber = 1;
    
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
                // Character names are CENTERED
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
                let regex = /\\([^)]+\\)/g;
                let match;
                
                while ((match = regex.exec(dialogueText)) !== null) {
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
                // Stage directions (parentheticals) are INDENTED and italicized
                let dirText = element.text;
                if (!dirText.startsWith('(')) {
                    dirText = '(' + dirText + ')';
                }
                content.push(new Paragraph({
                    spacing: { before: 0, after: 120 },
                    indent: { left: 1440 },  // Indent stage directions significantly
                    children: [new TextRun({ 
                        text: dirText, 
                        italics: true, 
                        size: 24, 
                        font: "Times New Roman" 
                    })]
                }));
                break;
            
            case 'action':
                // Action lines are INDENTED (like stage directions) and italicized
                content.push(new Paragraph({
                    spacing: { before: 120, after: 120 },
                    indent: { left: 1440 },  // Indented like stage directions
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
                    width: 12240,  // 8.5 inches
                    height: 15840   // 11 inches
                },
                margin: { 
                    top: 1440,    // 1 inch
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
    fs.writeFileSync("''' + output_path + '''", buffer);
    console.log("✓ Formatted play created successfully!");
});
'''
        
        # Write and execute JavaScript
        js_file = '/home/claude/format_play.js'
        with open(js_file, 'w') as f:
            f.write(js_code)
        
        try:
            subprocess.run(['node', js_file], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Error creating docx: {e}")
            sys.exit(1)


def main():
    print("=" * 60)
    print("PROFESSIONAL PLAY FORMATTER")
    print("Converts inconsistently formatted plays to industry standard")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python play_formatter.py <input.docx> [output.docx]")
        print()
        print("Example:")
        print("  python play_formatter.py my_play.docx")
        print("  python play_formatter.py my_play.docx formatted_play.docx")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.docx', '_FORMATTED.docx')
    
    # Ensure output has .docx extension
    if not output_file.endswith('.docx'):
        output_file += '.docx'
    
    if not Path(input_file).exists():
        print(f"✗ Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    if not input_file.endswith('.docx'):
        print(f"✗ Error: Input file must be a .docx file")
        print(f"  If you have a PDF, please convert it to Word format first")
        sys.exit(1)
    
    print(f"📄 Input file:  {input_file}")
    print(f"📝 Output file: {output_file}")
    print()
    print("Processing...")
    
    # Create formatter and process
    formatter = PlayFormatter()
    
    # Extract and parse
    text = formatter.extract_text_from_docx(input_file)
    metadata = formatter.extract_metadata(text)
    elements = formatter.parse_play(text)
    
    print(f"✓ Identified {len(elements)} play elements")
    print(f"✓ Found {len(formatter.character_names)} characters")
    print(f"✓ Title: {metadata.get('title', 'Unknown')}")
    print(f"✓ Author: {metadata.get('author', 'Unknown')}")
    print()
    
    # Create formatted output
    formatter.create_formatted_docx(elements, metadata, output_file)
    print(f"✓ Formatted play saved to: {output_file}")
    print()
    print("Done! Your play is now professionally formatted.")
    print("=" * 60)


if __name__ == '__main__':
    main()
