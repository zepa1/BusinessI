# QR Fiscal Receipt Reader

A Streamlit-based web application for reading and processing QR codes from fiscal receipts using your laptop's webcam.

## Features

- 📷 **Real-time Webcam Scanning**: Capture QR codes directly from your webcam
- 📤 **Image Upload**: Process QR codes from uploaded images
- 🔒 **Duplicate Prevention**: Automatically detects and prevents duplicate entries
- 💾 **CSV Storage**: Stores all access keys with timestamps in CSV format
- 📊 **Statistics Dashboard**: View collection statistics and recent scans
- 📥 **Data Export**: Download collected data as CSV

## Installation

1. Install the required dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

2. Run the application:
\`\`\`bash
streamlit run app.py
\`\`\`

## Usage

### Webcam Scanner
1. Click "Start Camera" to activate your webcam
2. Position the QR code in front of the camera
3. The app will automatically detect, extract, and save the access key
4. Click "Stop Camera" when finished

### Upload Image
1. Navigate to the "Upload Image" tab
2. Upload an image containing a QR code
3. Click "Process Image" to extract the access key

### View Data
- View all collected access keys in the "View Data" tab
- Download the CSV file from the sidebar
- Clear all data if needed

## Data Format

The application saves data in `access_keys.csv` with the following structure:
- `access_key`: The extracted 44-digit fiscal access key
- `timestamp`: Date and time of capture

## Technical Details

- **QR Code Detection**: Uses pyzbar library for robust QR code decoding
- **Webcam Access**: OpenCV for real-time video capture
- **Data Management**: Pandas for CSV operations and duplicate prevention
- **Web Interface**: Streamlit for user-friendly interface

## Troubleshooting

- **Camera not working**: Check browser permissions for camera access
- **QR code not detected**: Ensure good lighting and clear image quality
- **Duplicate warnings**: The system is working correctly - it prevents re-scanning the same receipt
