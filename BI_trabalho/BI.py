import streamlit as st
import cv2
from pyzbar import pyzbar
import pandas as pd
import os
from datetime import datetime
import numpy as np
from PIL import Image
import re

# Configuration
CSV_FILE = "access_keys.csv"

def load_existing_keys():
    """Load existing access keys from CSV file"""
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            return set(df['access_key'].tolist())
        except Exception as e:
            st.error(f"Error loading existing keys: {e}")
            return set()
    return set()

# Initialize session state
if 'access_keys' not in st.session_state:
    st.session_state.access_keys = load_existing_keys()
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

def save_to_csv(access_key):
    """Save access key to CSV file"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Validate access key
        if not access_key or len(access_key.strip()) == 0:
            st.error("Invalid access key: empty or null")
            return False
        
        # Create new entry
        new_entry = pd.DataFrame({
            'access_key': [access_key.strip()],
            'timestamp': [timestamp]
        })
        
        # Append to existing file or create new one
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            df = pd.concat([df, new_entry], ignore_index=True)
        else:
            df = new_entry
        
        df.to_csv(CSV_FILE, index=False)
        st.session_state.access_keys.add(access_key.strip())
        return True
        
    except Exception as e:
        st.error(f"Error saving access key: {e}")
        return False

def extract_access_key(qr_data):
    """Extract access key from QR code data"""
    # Fiscal QR codes typically contain the access key as a long numeric string
    # This function can be customized based on the specific QR code format
    
    if not qr_data or len(qr_data.strip()) == 0:
        return None
    
    # Try to find a 44-digit number (standard NFe access key length)
    matches = re.findall(r'\d{44}', qr_data)
    
    if matches:
        return matches[0]
    
    # Try to find other common access key patterns
    # 47-digit pattern (some fiscal systems)
    matches_47 = re.findall(r'\d{47}', qr_data)
    if matches_47:
        return matches_47[0]
    
    # Try to find any long numeric sequence (20+ digits)
    matches_long = re.findall(r'\d{20,}', qr_data)
    if matches_long:
        return matches_long[0]
    
    # If no numeric pattern found, return the full data if it's reasonable length
    if len(qr_data.strip()) <= 100:  # Reasonable length for access key
        return qr_data.strip()
    
    return None

def decode_qr_from_frame(frame):
    """Decode QR codes from a video frame"""
    decoded_objects = pyzbar.decode(frame)
    return decoded_objects

def process_uploaded_image(uploaded_file):
    """Process QR code from uploaded image"""
    try:
        # Validate file
        if uploaded_file is None:
            st.error("No file uploaded")
            return
        
        # Convert uploaded file to image
        image = Image.open(uploaded_file)
        image_np = np.array(image)
        
        # Validate image dimensions
        if image_np.size == 0:
            st.error("Invalid image: empty or corrupted")
            return
        
        # Convert to grayscale for better QR detection
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_np
        
        # Decode QR codes
        decoded_objects = pyzbar.decode(gray)
        
        if decoded_objects:
            for obj in decoded_objects:
                try:
                    qr_data = obj.data.decode('utf-8')
                    access_key = extract_access_key(qr_data)
                    
                    if access_key and access_key not in st.session_state.access_keys:
                        if save_to_csv(access_key):
                            st.success(f"✅ New access key saved: {access_key}")
                    else:
                        st.warning(f"⚠️ Duplicate detected: {access_key}")
                except UnicodeDecodeError:
                    st.error("❌ Could not decode QR code data")
                except Exception as e:
                    st.error(f"❌ Error processing QR code: {e}")
        else:
            st.error("❌ No QR code found in the image")
            
    except Exception as e:
        st.error(f"Error processing image: {e}")

# Streamlit UI
st.set_page_config(
    page_title="QR Fiscal Receipt Reader",
    page_icon="📱",
    layout="wide"
)

st.title("📱 QR Fiscal Receipt Reader")
st.markdown("**Business Intelligence Data Collection Tool**")

# Sidebar with statistics
with st.sidebar:
    st.header("📊 Statistics")
    st.metric("Total Keys Collected", len(st.session_state.access_keys))
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.metric("Total Scans", len(df))
        
        if st.button("📥 Download CSV"):
            with open(CSV_FILE, 'rb') as f:
                csv_data = f.read()
                st.download_button(
                    label="Download access_keys.csv",
                    data=csv_data,
                    file_name=CSV_FILE,
                    mime='text/csv'
                )
    
    st.divider()
    st.markdown("### 📋 Recent Keys")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        recent = df.tail(5).sort_values('timestamp', ascending=False)
        for _, row in recent.iterrows():
            st.text(f"{row['access_key'][:20]}...")
            st.caption(row['timestamp'])

# Main content
tab1, tab2, tab3 = st.tabs(["📷 Webcam Scanner", "📤 Upload Image", "📄 View Data"])

with tab1:
    st.header("Webcam QR Code Scanner")
    st.markdown("Position the QR code in front of your webcam")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🎥 Start Camera", type="primary"):
            st.session_state.camera_active = True
        
        if st.button("⏹️ Stop Camera"):
            st.session_state.camera_active = False
    
    with col1:
        camera_placeholder = st.empty()
        status_placeholder = st.empty()
    
    if st.session_state.camera_active:
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Could not access webcam. Please check your camera permissions.")
            st.session_state.camera_active = False
        else:
            try:
                status_placeholder.info("🔍 Scanning for QR codes...")
                
                # Capture frame
                ret, frame = cap.read()
                
                if ret:
                    # Decode QR codes
                    decoded_objects = decode_qr_from_frame(frame)
                    
                    # Draw rectangles around QR codes
                    for obj in decoded_objects:
                        try:
                            points = obj.polygon
                            if len(points) > 4:
                                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                                points = hull
                            
                            n = len(points)
                            for j in range(n):
                                cv2.line(frame, tuple(points[j]), tuple(points[(j+1) % n]), (0, 255, 0), 3)
                            
                            # Extract and save access key
                            qr_data = obj.data.decode('utf-8')
                            access_key = extract_access_key(qr_data)
                            
                            if access_key and access_key not in st.session_state.access_keys:
                                if save_to_csv(access_key):
                                    status_placeholder.success(f"✅ New key saved: {access_key}")
                            else:
                                status_placeholder.warning(f"⚠️ Duplicate: {access_key}")
                        except UnicodeDecodeError:
                            status_placeholder.error("❌ Could not decode QR code data")
                        except Exception as e:
                            status_placeholder.error(f"❌ Error processing QR code: {e}")
                    
                    # Display frame
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    camera_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                else:
                    status_placeholder.error("❌ Could not capture frame from camera")
                    
            except Exception as e:
                status_placeholder.error(f"❌ Camera error: {e}")
                st.session_state.camera_active = False
            finally:
                # Always release camera resources
                cap.release()
            
            # Auto-refresh for continuous scanning
            if st.session_state.camera_active:
                st.rerun()

with tab2:
    st.header("Upload QR Code Image")
    st.markdown("Upload an image containing a QR code from a fiscal receipt")
    
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=['png', 'jpg', 'jpeg', 'bmp'],
        help="Supported formats: PNG, JPG, JPEG, BMP"
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        with col2:
            if st.button("🔍 Process Image", type="primary"):
                process_uploaded_image(uploaded_file)

with tab3:
    st.header("Collected Access Keys")
    
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        
        st.markdown(f"**Total records:** {len(df)}")
        st.markdown(f"**Unique keys:** {df['access_key'].nunique()}")
        
        # Display data
        st.dataframe(
            df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear All Data"):
                if os.path.exists(CSV_FILE):
                    os.remove(CSV_FILE)
                    st.session_state.access_keys = set()
                    st.success("All data cleared!")
                    st.rerun()
    else:
        st.info("No data collected yet. Start scanning QR codes!")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>QR Fiscal Receipt Reader | Business Intelligence Tool</small>
    </div>
    """,
    unsafe_allow_html=True
)
