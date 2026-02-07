# PDF to HTML Converter 📄

A simple web app to convert PDF files to HTML while preserving formatting, figures, and layout.

[**🚀 Live Demo**](https://your-app.streamlit.app) *(add your URL after deployment)*

## Features

- ✅ Upload PDF files (up to 200MB)
- ✅ Converts to HTML with preserved formatting
- ✅ Download HTML file
- ✅ Preview converted HTML
- ✅ Customizable zoom and font embedding
- ✅ Works offline after download

## How to Use

1. Visit the app
2. Upload your PDF file
3. Click "Convert to HTML"
4. Download the HTML file
5. Open in any web browser!

## Deploy to Streamlit Cloud (Free)

1. **Fork this repository** or create a new one with these files:
   - `app.py`
   - `requirements.txt`
   - `packages.txt`

2. **Go to [share.streamlit.io](https://share.streamlit.io)**

3. **Click "New app"**

4. **Fill in:**
   - Repository: `your-username/your-repo`
   - Branch: `main`
   - Main file path: `app.py`

5. **Click "Deploy"**

Done! Your app will be live at `your-app.streamlit.app`

## Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Customize Fonts in Output

After downloading the HTML file:

1. Open it in a text editor
2. Find the `<head>` section
3. Add your custom CSS:

```html
<style>
body, p, div { 
    font-family: 'Your Font Name', sans-serif !important; 
}
</style>
```

## Tech Stack

- **Streamlit** - Web framework
- **pdf2htmlEX** - PDF to HTML conversion
- Python 3.11

## License

MIT

## Credits

Uses [pdf2htmlEX](https://github.com/pdf2htmlEX/pdf2htmlEX) for conversion.
