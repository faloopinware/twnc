import streamlit as st
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="The TWNC FaloopinFormatter",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 The TWNC FaloopinFormatter")
st.markdown("Format your play script to professional theatrical standards")

# Custom CSS for preview
st.markdown("""
<style>
    .preview-play {
        font-family: 'Times New Roman', serif;
        font-size: 12pt;
        line-height: 1.5;
        max-width: 700px;
        margin: 0 auto;
        background-color: white;
        padding: 40px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    .preview-character {
        text-align: center;
        margin-top: 12pt;
        margin-bottom: 0;
    }
    .preview-dialogue {
        text-align: left;
        margin: 0;
    }
    .preview-stage {
        font-style: italic;
        margin: 6pt 0;
    }
    .preview-title {
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with instructions
with st.sidebar:
    st.header("📋 Formatting Guide")
    st.markdown("""
    **How to format your script:**
    
    - **Title Page:** Enter play title and author
    - **Scene Info:** Add scene or act information
    - **Character Names:** Type in ALL CAPS on their own line
    - **Inline Stage Directions:** Use (parentheses) on same line as dialogue
    - **Standalone Stage Directions:** Put on separate line in (parentheses)
    - **Setting:** Opening description in italics
    
    **Example:**
    ```
    ACT ONE
    
    SETTING: A bedroom at night
    
    (JOHN enters nervously)
    
    JOHN
    I can't believe that.
    
    MARY
    (softly) What do you mean?
    ```
    
    **Output Format:**
    - Cover page with title and author
    - Page numbers in upper right (starting page 1)
    - Times New Roman 12pt
    - Character names centered (not bold)
    - Dialogue left-aligned (not indented)
    """)
    
    st.info("💡 **Cloud Version**: Exports .docx only. Open in Word and Save As PDF if needed.")

def parse_script_to_structure(text):
    """Parse raw script text into structured data"""
    lines = text.strip().split('\n')
    elements = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Scene headings
        if re.match(r'^(ACT|SCENE|PROLOGUE|EPILOGUE)\s+', line, re.IGNORECASE):
            elements.append({
                'type': 'scene_heading',
                'text': line
            })
        # Character names (all caps, short, followed by dialogue)
        elif line.isupper() and len(line.split()) <= 5 and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.isupper():
                elements.append({
                    'type': 'character',
                    'text': line
                })
        # Standalone stage direction
        elif line.startswith('(') and line.endswith(')'):
            if elements and elements[-1]['type'] != 'character':
                elements.append({
                    'type': 'stage_direction',
                    'text': line
                })
            else:
                elements.append({
                    'type': 'dialogue',
                    'text': line
                })
        # Setting/description keywords
        elif re.match(r'^(SETTING:|TIME:|AT RISE|LIGHTS UP)', line, re.IGNORECASE):
            elements.append({
                'type': 'setting',
                'text': line
            })
        # Dialogue
        else:
            elements.append({
                'type': 'dialogue',
                'text': line
            })
        
        i += 1
    
    return elements

def create_docx_document(title, author, scene_info, elements):
    """Create a Word document using python-docx"""
    
    doc = Document()
    
    # Set default font to Times New Roman 12pt
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Set page margins (1 inch all around)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # COVER PAGE
    # Add some space from top
    for _ in range(8):
        doc.add_paragraph()
    
    # Title
    if title:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    
    # "By"
    if author:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("By")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Author name
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(author)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    
    # PAGE BREAK to start script on new page
    doc.add_page_break()
    
    # SCRIPT PAGES
    # Add scene info at top of first script page
    if scene_info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(scene_info)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        
        # Add space after scene heading
        doc.add_paragraph()
    
    # Process each element
    for element in elements:
        if element['type'] == 'character':
            # Character name - centered, not bold
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.space_before = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            
        elif element['type'] == 'dialogue':
            # Dialogue - left-aligned, parse inline stage directions
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            text = element['text']
            pattern = r'(\([^)]+\))'
            segments = re.split(pattern, text)
            
            for segment in segments:
                if segment:
                    run = p.add_run(segment)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(12)
                    
                    # Italicize if it's a stage direction
                    if segment.startswith('(') and segment.endswith(')'):
                        run.italic = True
        
        elif element['type'] == 'stage_direction':
            # Standalone stage direction - italics
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.space_before = Pt(6)
            p.space_after = Pt(6)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.italic = True
        
        elif element['type'] == 'scene_heading':
            # Scene/Act heading - centered
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.space_before = Pt(24)
            p.space_after = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        
        elif element['type'] == 'setting':
            # Setting description - italics
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.space_before = Pt(12)
            p.space_after = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.italic = True
    
    # Add END marker
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.space_before = Pt(24)
    run = p.add_run("— END —")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.italic = True
    
    # Add page numbers to header (except first page)
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    
    # Header for pages after first (with page number)
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run()
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    
    # Save to BytesIO object
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    return bio

# Main tabs
tab1, tab2, tab3 = st.tabs(["✍️ Write/Edit", "👁️ Preview", "📤 Export"])

with tab1:
    st.header("Enter Your Play")
    
    col1, col2 = st.columns(2)
    
    with col1:
        play_title = st.text_input("Play Title*", placeholder="HAMLET")
        author = st.text_input("Author*", placeholder="William Shakespeare")
    
    with col2:
        scene_info = st.text_input("Scene/Act Info", placeholder="Scene One of One", help="This will appear at top of first script page")
    
    # Example script button
    if st.button("📝 Load Example Script"):
        st.session_state['script_content'] = """SETTING: A living room, present day.

(SARAH sits reading. MICHAEL enters)

SARAH
(looking up from her book) Did you hear that?

MICHAEL
Hear what?

SARAH
(standing) That sound. Like someone crying.

MICHAEL
(dismissively) It's just the wind, Sarah.

SARAH
No, it's more than that. (walks to window) There's someone out there.

MICHAEL
You're imagining things again."""
    
    script_content = st.text_area(
        "Script Content*",
        value=st.session_state.get('script_content', ''),
        height=450,
        placeholder="Enter your script here...\n\nJOHN\n(enters) Hello, world!"
    )
    
    if script_content:
        st.session_state['script_content'] = script_content
        st.session_state['play_title'] = play_title
        st.session_state['author'] = author
        st.session_state['scene_info'] = scene_info

with tab2:
    st.header("Preview")
    
    if 'script_content' in st.session_state and st.session_state['script_content']:
        preview_html = '<div class="preview-play">'
        
        if st.session_state.get('play_title'):
            preview_html += f'<div class="preview-title"><strong>{st.session_state["play_title"]}</strong></div>'
        if st.session_state.get('author'):
            preview_html += f'<div class="preview-title">By<br/>{st.session_state["author"]}</div>'
        
        preview_html += '<hr style="margin: 40px 0;"/>'
        
        if st.session_state.get('scene_info'):
            preview_html += f'<div class="preview-title"><strong>{st.session_state["scene_info"]}</strong></div>'
        
        elements = parse_script_to_structure(st.session_state['script_content'])
        
        for element in elements:
            if element['type'] == 'character':
                preview_html += f'<p class="preview-character">{element["text"]}</p>'
            elif element['type'] == 'dialogue':
                text = element['text']
                formatted_text = re.sub(r'\(([^)]+)\)', r'<em>(\1)</em>', text)
                preview_html += f'<p class="preview-dialogue">{formatted_text}</p>'
            elif element['type'] == 'stage_direction':
                preview_html += f'<p class="preview-stage">{element["text"]}</p>'
            elif element['type'] == 'scene_heading':
                preview_html += f'<p class="preview-title"><strong>{element["text"]}</strong></p>'
            elif element['type'] == 'setting':
                preview_html += f'<p class="preview-stage">{element["text"]}</p>'
        
        preview_html += '</div>'
        st.markdown(preview_html, unsafe_allow_html=True)
    else:
        st.info("👈 Enter your script in the Write/Edit tab to see a preview")

with tab3:
    st.header("Export Your Script")
    
    if 'script_content' in st.session_state and st.session_state['script_content']:
        
        # Check for required fields
        if not st.session_state.get('play_title') or not st.session_state.get('author'):
            st.warning("⚠️ Please enter both Play Title and Author in the Write/Edit tab")
        else:
            filename = st.text_input(
                "Filename",
                value=st.session_state.get('play_title', 'my_play').replace(' ', '_').lower(),
                help="Enter filename without extension"
            )
            
            if st.button("🎭 Generate Word Document", type="primary"):
                try:
                    with st.spinner("Creating your professionally formatted script..."):
                        # Parse the script
                        elements = parse_script_to_structure(st.session_state['script_content'])
                        
                        # Create the document
                        doc_file = create_docx_document(
                            st.session_state.get('play_title', ''),
                            st.session_state.get('author', ''),
                            st.session_state.get('scene_info', ''),
                            elements
                        )
                        
                        st.success("✅ Document created successfully!")
                        
                        # Provide download button
                        st.download_button(
                            label="📥 Download Word Document (.docx)",
                            data=doc_file,
                            file_name=f"{filename}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        
                        st.divider()
                        st.info("""
                        ✨ **Your script is formatted with:**
                        - Professional cover page with title and author
                        - Page numbers in upper right corner (starting page 1)
                        - Times New Roman 12pt font
                        - Character names centered (not bold)
                        - Dialogue left-aligned (not indented)
                        - Inline stage directions on same line
                        - Scene/Act info at top of first script page
                        
                        💡 **To create a PDF:**
                        1. Download the .docx file
                        2. Open in Microsoft Word or Google Docs
                        3. File → Save As → PDF
                        """)
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter your script in the Write/Edit tab first")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 40px;'>
    <p>The TWNC FaloopinFormatter | Industry-Standard Theatrical Formatting</p>
    <p>Cloud version - Exports to Microsoft Word (.docx)</p>
</div>
""", unsafe_allow_html=True)
