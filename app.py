import streamlit as st
import subprocess
import os
import tempfile
import shutil

st.set_page_config(
    page_title="PDF to HTML Converter",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF to HTML Converter")
st.markdown("Convert your PDF files to HTML while preserving formatting, figures, and layout.")

@st.cache_resource
def setup_pdf2htmlex():
    """Download and extract pdf2htmlEX AppImage (FUSE-less extraction)"""
    
    extracted_dir = "/tmp/pdf2htmlex_extracted"
    apprun_path = f"{extracted_dir}/AppRun"
    
    # Check if already extracted
    if os.path.exists(apprun_path):
        return apprun_path
    
    try:
        with st.spinner("Setting up pdf2htmlEX (first time only)..."):
            appimage_path = "/tmp/pdf2htmlEX.AppImage"
            
            # Download AppImage
            if not os.path.exists(appimage_path):
                url = "https://github.com/pdf2htmlEX/pdf2htmlEX/releases/download/v0.18.8.rc1/pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.AppImage"
                
                result = subprocess.run(
                    ['wget', '-q', '-O', appimage_path, url],
                    capture_output=True,
                    timeout=120
                )
                
                if result.returncode != 0:
                    st.error("Failed to download pdf2htmlEX")
                    return None
                
                subprocess.run(['chmod', '+x', appimage_path], check=True)
            
            # Extract AppImage (no FUSE needed!)
            os.makedirs(extracted_dir, exist_ok=True)
            
            result = subprocess.run(
                [appimage_path, '--appimage-extract'],
                cwd='/tmp',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Move extracted contents
            if os.path.exists('/tmp/squashfs-root'):
                if os.path.exists(extracted_dir):
                    shutil.rmtree(extracted_dir)
                shutil.move('/tmp/squashfs-root', extracted_dir)
            
            if os.path.exists(apprun_path):
                subprocess.run(['chmod', '+x', apprun_path], check=True)
                st.success("Setup complete!")
                return apprun_path
            else:
                st.error(f"Extraction failed. AppRun not found at {apprun_path}")
                return None
            
    except Exception as e:
        st.error(f"Setup error: {e}")
        return None

# Sidebar options
with st.sidebar:
    st.header("⚙️ Options")
    zoom = st.slider("Zoom Level", 0.5, 2.0, 1.3, 0.1, 
                     help="Adjust text size in output")
    embed_fonts = st.checkbox("Embed Fonts", value=True,
                              help="Include fonts in HTML file")
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Uses [pdf2htmlEX](https://github.com/pdf2htmlEX/pdf2htmlEX) to convert PDFs to HTML")

# Main content
uploaded_file = st.file_uploader(
    "Upload your PDF file",
    type=['pdf'],
    help="Maximum file size: 200MB"
)

if uploaded_file is not None:
    # Show file info
    file_size = uploaded_file.size / 1024 / 1024  # MB
    st.info(f"📎 **{uploaded_file.name}** ({file_size:.2f} MB)")
    
    # Convert button
    if st.button("🔄 Convert to HTML", type="primary", use_container_width=True):
        
        # Setup pdf2htmlEX
        pdf2htmlex = setup_pdf2htmlex()
        
        if pdf2htmlex is None:
            st.error("❌ Could not setup pdf2htmlEX. Please refresh and try again.")
            st.stop()
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                # Save uploaded PDF
                pdf_path = os.path.join(tmpdir, "input.pdf")
                with open(pdf_path, 'wb') as f:
                    f.write(uploaded_file.read())
                
                st.write("### Debug Info")
                st.write(f"PDF saved to: {pdf_path}")
                st.write(f"PDF exists: {os.path.exists(pdf_path)}")
                st.write(f"PDF size: {os.path.getsize(pdf_path)} bytes")
                
                # Check extraction directory
                st.write(f"Extracted dir exists: {os.path.exists('/tmp/pdf2htmlex_extracted')}")
                
                # Search for manifest file
                manifest_location = None
                data_dir = None
                
                # Try the correct location first
                correct_location = '/tmp/pdf2htmlex_extracted/usr/local/share/pdf2htmlEX'
                if os.path.exists(correct_location):
                    data_dir = correct_location
                    st.write(f"✓ Found data dir at: {data_dir}")
                else:
                    st.write("Searching for manifest file...")
                    for root, dirs, files in os.walk('/tmp/pdf2htmlex_extracted'):
                        if 'manifest' in files:
                            manifest_location = root
                            st.write(f"✓ Found manifest in: {root}")
                            st.write(f"  Files: {files}")
                            data_dir = root
                            break
                
                if not data_dir:
                    st.error("Could not find pdf2htmlEX data directory!")
                    st.stop()
                
                # Build conversion command
                output_name = "output.html"
                
                # Set environment for AppRun to find data files
                env = os.environ.copy()
                env['APPDIR'] = '/tmp/pdf2htmlex_extracted'
                
                cmd = [
                    pdf2htmlex,
                    f'--data-dir={data_dir}',
                    f'--zoom={zoom}',
                ]
                
                if not embed_fonts:
                    cmd.append('--embed-font=0')
                
                cmd.extend([pdf_path, output_name])
                
                st.write("### Command to execute:")
                st.code(' '.join(cmd))
                
                # Run conversion
                with st.spinner("Converting... This may take a moment."):
                    result = subprocess.run(
                        cmd,
                        cwd=tmpdir,
                        capture_output=True,
                        text=True,
                        timeout=300,
                        env=env
                    )
                
                # Debug: Show what happened
                st.write(f"Return code: {result.returncode}")
                if result.stdout:
                    st.write("STDOUT:", result.stdout)
                if result.stderr:
                    st.write("STDERR:", result.stderr)
                
                # Check if conversion succeeded
                output_html = os.path.join(tmpdir, output_name)
                
                # Debug: Check what files were created
                st.write("Files in tmpdir:", os.listdir(tmpdir))
                
                if os.path.exists(output_html):
                    file_size = os.path.getsize(output_html)
                    st.write(f"Output HTML size: {file_size} bytes")
                    
                    if file_size == 0:
                        st.error("❌ Output file is empty!")
                        st.write("Command:", ' '.join(cmd))
                        st.stop()
                    
                    # Read the HTML file
                    with open(output_html, 'r', encoding='utf-8', errors='ignore') as f:
                        html_content = f.read()
                    
                    # Success!
                    st.success("✅ Conversion complete!")
                    
                    # Download button
                    output_filename = uploaded_file.name.replace('.pdf', '.html')
                    st.download_button(
                        label="📥 Download HTML File",
                        data=html_content,
                        file_name=output_filename,
                        mime='text/html',
                        use_container_width=True
                    )
                    
                    # Optional preview
                    with st.expander("👁️ Preview HTML (click to expand)"):
                        st.components.v1.html(html_content, height=600, scrolling=True)
                    
                    # Tips
                    with st.expander("💡 Tips for customizing your HTML"):
                        st.markdown("""
                        **Change fonts:**
                        1. Open the downloaded HTML in a text editor
                        2. Find the `<head>` section
                        3. Add this CSS:
                        ```html
                        <style>
                        body, p, div { 
                            font-family: 'Your Font Name', sans-serif !important; 
                        }
                        </style>
                        ```
                        
                        **View in browser:**
                        - Simply open the HTML file in any web browser
                        - Works offline - no internet needed!
                        """)
                
                else:
                    # Conversion failed
                    st.error("❌ Conversion failed")
                    
                    with st.expander("Show error details"):
                        st.code(result.stderr)
                        st.code(result.stdout)
            
            except subprocess.TimeoutExpired:
                st.error("❌ Conversion timed out. Your PDF might be too large or complex.")
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                with st.expander("Show error details"):
                    st.exception(e)

else:
    # Instructions when no file uploaded
    st.info("👆 Upload a PDF file to get started")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. Upload your PDF file
        2. Click "Convert to HTML"
        3. Download the HTML file
        4. Open it in any web browser!
        
        **Features:**
        - Preserves formatting, images, and layout
        - Creates a single HTML file
        - Works offline after download
        - Optional font embedding
        """)
