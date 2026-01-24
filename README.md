# 🎭 The TWNC FaloopinFormatter - Cloud Version

**Streamlit Cloud-Compatible Play Formatter**

Format your play scripts to professional theatrical standards with automatic Word document generation.

## 🌐 Live Demo

This version is optimized for deployment on **Streamlit Cloud** and works entirely in the browser!

## ✨ Features

### Professional Theatrical Formatting:
- ✅ **Cover page** with title, "By", and author name
- ✅ **Page numbers** in upper right corner (starting page 1 on script pages)
- ✅ **Times New Roman 12pt** for all text
- ✅ **Character names centered** (NOT bolded)
- ✅ **Dialogue left-aligned** (NOT indented)
- ✅ **Inline stage directions** stay on the same line as dialogue
- ✅ **Standalone stage directions** in italics on their own line
- ✅ **Scene/Act info** at top of first script page
- ✅ **Instant Word export** - download .docx files directly

## 🚀 Deploy to Streamlit Cloud

### Quick Deploy:

1. **Fork this repository** or upload these files to your GitHub repo:
   - `streamlit_app.py`
   - `requirements.txt`

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"**

4. **Connect your GitHub** and select:
   - Your repository
   - Branch: `main` (or your branch name)
   - Main file path: `streamlit_app.py`

5. **Click "Deploy"**

That's it! Your app will be live in minutes.

## 💻 Run Locally

```bash
# Install requirements
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

## 📝 How to Use

### 1. Enter Play Information (Write/Edit Tab)

**Required:**
- Play Title (e.g., "HAMLET")
- Author (e.g., "William Shakespeare")

**Optional:**
- Scene/Act Info (e.g., "Scene One of One")

### 2. Write Your Script

**Character Names:** Type in ALL CAPS on their own line
```
JOHN
```

**Inline Stage Directions:** Use (parentheses) on same line
```
MARY
(softly) I can't believe it.
```

**Standalone Stage Directions:** On separate line
```
(She walks to the window)
```

**Setting Description:**
```
SETTING: A bedroom at night

(JOHN enters nervously)
```

### 3. Preview (Preview Tab)

See how your formatted script will look.

### 4. Export (Export Tab)

Click "Generate Word Document" and download your professionally formatted .docx file!

## 📄 Example Output

### Cover Page:
```
GAME TALK

By
Lindsey Salatka
```

### First Script Page (with page number):
```
                                                                    1

Scene One of One

KATHRYN, a 50-year-old sporty mom...

(Kathryn hands Angela a pom pom)

                    KATHRYN
Five minutes left in the first...
```

## 📊 Format Specifications

| Element | Format |
|---------|--------|
| Font | Times New Roman 12pt |
| Cover page | Title, "By", Author (centered) |
| Page numbers | Upper right, starting page 1 |
| Character names | Centered, NOT bold |
| Dialogue | Left-aligned, NOT indented |
| Stage directions | Italics (inline or standalone) |

## 📥 Creating PDFs

Since the cloud version exports .docx only, here's how to create PDFs:

### Option 1: Microsoft Word
1. Download the .docx file
2. Open in Word
3. File → Save As → PDF

### Option 2: Google Docs
1. Upload the .docx to Google Drive
2. Open with Google Docs
3. File → Download → PDF Document

## 🎯 Professional Standards

This formatter follows **industry-standard theatrical formatting**:
- ✅ Used by professional theaters
- ✅ Accepted by playwriting contests
- ✅ Standard for script submissions
- ✅ Easy to read during rehearsals

## 📦 Files Included

- `streamlit_app.py` - Main application
- `requirements.txt` - Python dependencies
- `README.md` - This file

## 💡 Tips for Best Results

1. **Fill in all required fields** (Title and Author)
2. **Preview before exporting** - Check the Preview tab
3. **Use ALL CAPS for character names** 
4. **Put inline directions in (parentheses)**
5. **Load the example** to see proper formatting

---

**Ready to format your plays professionally!** 🎭✨

*Cloud version - Deploy anywhere, format everywhere!*
