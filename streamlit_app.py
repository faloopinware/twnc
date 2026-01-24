import streamlit as st
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import PyPDF2

# Page configuration
st.set_page_config(
    page_title="The TWNC FaloopinFormatter",
    page_icon="🎭",
    layout="wide"
)

st.title("🎭 The TWNC FaloopinFormatter")
st.markdown("Upload your script and we'll reformat it to professional theatrical standards")

# Sidebar
with st.sidebar:
    st.header("📋 How It Works")
    st.markdown("""
    **3 Simple Steps:**
    
    **1️⃣ Upload Your Script**
    - PDF, DOCX, or TXT file
    - We'll read and analyze it
    
    **2️⃣ Enter Details**
    - Provide title and author
    - We'll detect most info automatically
    
    **3️⃣ Download**
    - Get your professionally formatted .DOCX file
    - Open in Word, Google Docs, or any word processor
    
    ---
    
    **What We Fix:**
    - ✅ Add proper cover page
    - ✅ Add page numbers
    - ✅ Format character names (centered)
    - ✅ Format dialogue (left-aligned)
    - ✅ Format stage directions (italics)
    - ✅ Times New Roman 12pt throughout
    """)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF - keep lines separate, let parser handle structure"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        all_text = []
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            all_text.append(page_text)
        
        # Join all pages and return
        return "\n".join(all_text)
    
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        st.error(f"Error reading TXT: {str(e)}")
        return None

def parse_script_intelligently(text):
    """Parse script text - handles messy PDF extraction"""
    raw_lines = [l.strip() for l in text.split('\n') if l.strip() and not l.strip().isdigit()]
    
    # Common character names
    common_names = {'JOHN', 'MARY', 'KATE', 'MIKE', 'SARAH', 'TOM', 'JANE', 'BOB',
                   'KATHRYN', 'ANGELA', 'MICHAEL', 'SUSAN', 'DAVID', 'LISA', 'TRUDY',
                   'PETER', 'EMMA', 'CHRIS', 'ANNA', 'JAMES'}
    
    # First, merge fragments into logical lines
    merged_lines = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        
        # Check if this is a character name
        is_char_name = False
        if line.isupper() and not line.startswith('('):
            words = len(line.split())
            if 2 <= words <= 5 or (words == 1 and line in common_names):
                # Look ahead - if next line isn't all caps, this is a character name
                if i + 1 < len(raw_lines):
                    next_line = raw_lines[i + 1]
                    if not next_line.isupper() or next_line.startswith('('):
                        is_char_name = True
        
        if is_char_name:
            merged_lines.append(line)
            i += 1
        else:
            # Merge short fragments
            merged = line
            i += 1
            
            while i < len(raw_lines):
                next_line = raw_lines[i]
                
                # Stop if next is character name
                if next_line.isupper() and not next_line.startswith('('):
                    nw = len(next_line.split())
                    if 2 <= nw <= 5 or (nw == 1 and next_line in common_names):
                        if i + 1 < len(raw_lines) and not raw_lines[i + 1].isupper():
                            break
                
                # Stop if we have complete sentence
                if merged.rstrip().endswith(('.', '!', '?', ')')):
                    break
                
                # Stop if long enough
                if len(merged) > 200:
                    break
                
                # Merge the fragment
                if next_line in [',', '.', '!', '?', ':', ';']:
                    merged += next_line
                else:
                    merged += " " + next_line
                i += 1
            
            merged_lines.append(merged)
    
    # Now parse the merged lines
    elements = []
    title = None
    author = None
    scene_info = None
    script_start = 0
    
    # Find title, author, scene info
    for i, line in enumerate(merged_lines[:15]):
        if not title and len(line) < 60 and not line.startswith('By') and not line.isupper():
            title = line
            script_start = i + 1
        elif title and not author:
            if line.startswith('By'):
                author = line.replace('By', '').strip()
                script_start = i + 1
            elif len(line) < 60 and not line.isupper():
                author = line
                script_start = i + 1
        elif re.match(r'(Scene|ACT|Act)', line, re.IGNORECASE):
            scene_info = line
            script_start = i + 1
            break
    
    # Parse script content
    for line in merged_lines[script_start:]:
        # Scene headings
        if re.match(r'^(ACT|SCENE|PROLOGUE|EPILOGUE)', line, re.IGNORECASE):
            elements.append({'type': 'scene_heading', 'text': line})
        # Setting
        elif re.match(r'^(SETTING:|TIME:|AT RISE:|LIGHTS UP)', line, re.IGNORECASE):
            elements.append({'type': 'setting', 'text': line})
        # Character names
        elif line.isupper() and not line.startswith('('):
            words = len(line.split())
            if 2 <= words <= 5 or (words == 1 and line in common_names):
                elements.append({'type': 'character', 'text': line})
        # Stage directions
        elif line.startswith('(') and line.endswith(')'):
            if elements and elements[-1]['type'] == 'character':
                elements.append({'type': 'dialogue', 'text': line})
            else:
                elements.append({'type': 'stage_direction', 'text': line})
        # Dialogue
        else:
            elements.append({'type': 'dialogue', 'text': line})
    
    return title, author, scene_info, elements

def create_formatted_docx(title, author, scene_info, elements):
    """Create professionally formatted Word document"""
    
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    
    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # COVER PAGE
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
        
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(author)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    
    # Page break
    doc.add_page_break()
    
    # Scene info at top of first script page
    if scene_info:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(scene_info)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        doc.add_paragraph()
    
    # Process elements
    for element in elements:
        if element['type'] == 'character':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.space_before = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            
        elif element['type'] == 'dialogue':
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
                    if segment.startswith('(') and segment.endswith(')'):
                        run.italic = True
        
        elif element['type'] == 'stage_direction':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.space_before = Pt(6)
            p.space_after = Pt(6)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.italic = True
        
        elif element['type'] == 'scene_heading':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.space_before = Pt(24)
            p.space_after = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
        
        elif element['type'] == 'setting':
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.space_before = Pt(12)
            p.space_after = Pt(12)
            run = p.add_run(element['text'])
            run.font.name = 'Times New Roman'
            run.font.size = Pt(12)
            run.italic = True
    
    # END marker
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.space_before = Pt(24)
    run = p.add_run("— END —")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.italic = True
    
    # Page numbers
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    header = section.header
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    
    # Save to BytesIO
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    
    return bio

# Main interface
st.header("🎭 Reformat Your Script in 3 Easy Steps")

# STEP 1: Upload
st.subheader("📤 Step 1: Upload Your Script File")

uploaded_file = st.file_uploader(
    "Choose your script file (PDF, DOCX, or TXT)",
    type=['pdf', 'docx', 'txt'],
    help="Upload a PDF, Word document, or text file"
)

if uploaded_file:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    
    # Extract text based on file type
    with st.spinner("Reading your script..."):
        if uploaded_file.name.endswith('.pdf'):
            script_text = extract_text_from_pdf(uploaded_file)
        elif uploaded_file.name.endswith('.docx'):
            script_text = extract_text_from_docx(uploaded_file)
        elif uploaded_file.name.endswith('.txt'):
            script_text = extract_text_from_txt(uploaded_file)
        else:
            st.error("Unsupported file type")
            script_text = None
    
    if script_text:
        st.success("✅ Script loaded successfully!")
        
        # Show preview of original
        with st.expander("📄 View Original Text (First 500 characters)"):
            st.text(script_text[:500] + "..." if len(script_text) > 500 else script_text)
        
        # Parse the script
        with st.spinner("Analyzing script structure..."):
            title, author, scene_info, elements = parse_script_intelligently(script_text)
        
        st.info(f"✨ Detected {len(elements)} script elements" + (f" | Scene: {scene_info}" if scene_info else ""))
        
        # STEP 2: Enter title and author
        st.divider()
        st.subheader("✏️ Step 2: Please Enter the Title and Author's Name")
        
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Play Title*", value=title or "", placeholder="e.g., HAMLET")
        with col2:
            author = st.text_input("Author*", value=author or "", placeholder="e.g., William Shakespeare")
        
        # STEP 3: Download
        st.divider()
        st.subheader("📥 Step 3: Download Your Formatted Script")
        
        if not title or not author:
            st.warning("⚠️ Please enter both Title and Author above to continue")
        else:
            filename = st.text_input(
                "Filename (optional - will use title if blank)",
                value="",
                placeholder=title.replace(' ', '_').lower() if title else "my_play"
            )
            
            # Use title as filename if not provided
            if not filename:
                filename = title.replace(' ', '_').lower() if title else "formatted_script"
            
            if st.button("📄 Download as .DOCX", type="primary", use_container_width=True):
                with st.spinner("Creating Word document..."):
                    formatted_doc = create_formatted_docx(title, author, scene_info, elements)
                
                st.success("✅ Document created!")
                
                st.download_button(
                    label="💾 Save Word Document",
                    data=formatted_doc,
                    file_name=f"{filename}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            
            st.divider()
            st.success("""
            ✨ **Your script will be formatted with:**
            - Professional cover page with title and author
            - Page numbers in upper right corner (starting page 1)
            - Times New Roman 12pt font throughout
            - Character names centered (not bold)
            - Dialogue left-aligned (not indented)
            - Stage directions properly formatted in italics
            - Scene/Act info at top of first script page
            """)

else:
    st.info("👆 Upload a script file above to get started")
    
    st.markdown("""
    ### 📝 Supported Formats:
    - **PDF** (.pdf) - Most common
    - **Word** (.docx) - Microsoft Word documents
    - **Text** (.txt) - Plain text files
    
    ### ✨ What We'll Fix:
    1. Add professional cover page
    2. Add page numbers in upper right corner
    3. Format character names (centered, not bold)
    4. Format dialogue (left-aligned, not indented)
    5. Format stage directions (italics, inline or standalone)
    6. Apply Times New Roman 12pt throughout
    7. Add proper spacing and margins
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 40px;'>
    <p>The TWNC FaloopinFormatter | Professional Script Reformatting</p>
    <p>Upload → Enter Details → Download (.DOCX)</p>
</div>
""", unsafe_allow_html=True)
