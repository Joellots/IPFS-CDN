import streamlit as st
import requests
from PIL import Image

st.set_page_config(
    page_title="IPFS Cluster Dashboard",
    page_icon="🌟",
    layout="centered"
)

# IPFS Cluster API Base
GATEWAY_BASE = 'http://127.0.0.1/ipfs'
CLUSTER_API_BASE = 'http://127.0.0.1/api/v0'  

# Check if any node is up
def check_cluster_status():
    try:
        response = requests.get(f"{CLUSTER_API_BASE}/pin/ls", timeout=5)
        if response.status_code == 200:
            st.success("IPFS Cluster nodes are up and running!")
        else:
            st.error("IPFS Cluster nodes appear to be down. Please check the nodes.")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to the IPFS Cluster: {e}")
        st.stop()

# Check cluster status before rendering the app
check_cluster_status()

# Welcome text
st.title("🔮 :grey[InterPlanetary File System]")

# Display Image
webp_image = Image.open("/home/joel/Desktop/ipfs_logo_main.jpeg")
image = webp_image.convert("RGB")
st.image(image, caption="IPFS", width=800)

st.markdown(
    """
    Welcome to the **IPFS Cluster Dashboard**! This application allows you to interact with your IPFS cluster easily. Below, you will find expandable sections for each functionality. Click on a section to expand it and perform operations such as:
    - Pin files across all cluster nodes
    - List pinned files
    - Perform garbage collection
    - Fetch and display file content
    """
)

# Functions
def upload_and_pin_file():
    with st.expander("Upload and Pin File"):
        uploaded_file = st.file_uploader("Choose a file to upload", type=None)
        if uploaded_file is not None:
            with st.spinner("Uploading file to cluster..."):
                try:
                    # Upload file to the cluster
                    files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{CLUSTER_API_BASE}/add", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        cid = result["Hash"]  # Cluster uses "cid" instead of "Hash"
                        st.success(f"File uploaded to cluster with CID: {cid}")
                    else:
                        st.error(f"Failed to upload file: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

def list_pinned_files():
    with st.expander("List Cluster Pinned Files"):
        if st.button("Fetch Pinned Files"):
            with st.spinner("Fetching pinned files from the cluster..."):
                try:
                    response = requests.get(f"{CLUSTER_API_BASE}/pin/ls")
                    if response.status_code == 200:
                        pinned_files = response.json().get("Keys", {})
                        if pinned_files:
                            st.success("Pinned files retrieved successfully!")
                            formatted_data = [
                                {"CID": cid, "Type": details.get("Type", "Unknown")}
                                for cid, details in pinned_files.items()
                            ]
                            st.write("Pinned Files:")
                            for item in formatted_data:
                                st.markdown(f"**CID**: `{item['CID']}` - **Type**: {item['Type']}")
                        else:
                            st.info("No pinned files found.")
                    else:
                        st.error(f"Failed to retrieve pinned files: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")



def unpin_file():
    with st.expander("Unpin File"):
        cid = st.text_input("Enter CID to unpin")
        if st.button("Unpin File"):
            with st.spinner("Unpinning file from the cluster..."):
                try:
                    response = requests.get(f"{CLUSTER_API_BASE}/pin/rm/{cid}")
                    if response.status_code == 200:
                        st.success(f"File with CID {cid} unpinned from the cluster.")
                    else:
                        st.error(f"Failed to unpin file: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

def perform_garbage_collection():
    with st.expander("Perform Garbage Collection"):
        if st.button("Run Garbage Collection"):
            with st.spinner("Performing garbage collection on the cluster..."):
                try:
                    response = requests.get(f"{CLUSTER_API_BASE}/repo/gc")
                    if response.status_code == 200:
                        if not response.text.strip():
                            st.success("No Gabbage Collection Needed!")
                        else:
                            st.success("Garbage collection completed successfully!")                        
                    else:
                        st.error(f"Failed to perform garbage collection: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

def view_file_content():
    with st.expander("View File Content"):
        cid = st.text_input("Enter CID to view file content")
        if st.button("View File Content"):
            with st.spinner("Fetching file content from the cluster..."):
                try:
                    pinned_response = requests.get(f"{CLUSTER_API_BASE}/pin/ls")
                    pinned_files = pinned_response.json().get("Keys", {})

                    CIDS = [cid for cid, details in pinned_files.items()]                          
                    if cid in CIDS:
                        response = requests.get(f"{GATEWAY_BASE}/{cid}", stream=True)
                        if response.status_code == 200:
                            # Detect Content Type
                            content_type = response.headers.get('Content-Type', 'application/octet-stream')
                            content_disposition = response.headers.get('Content-Disposition', '')

                            # Extract filename from Content-Disposition if available
                            file_name = None
                            if 'filename=' in content_disposition:
                                file_name = content_disposition.split('filename=')[1].strip('"')

                            # Fallback to CID-based naming if filename is not provided
                            if not file_name:
                                file_name = f"{cid[:8]}.{content_type.split('/')[-1]}"

                            # Display file based on type
                            if 'text' in content_type:
                                st.success(f"Content of {file_name} retrieved successfully!")
                                st.text(response.text)
                            elif 'image' in content_type:
                                st.success(f"Displaying image: {file_name}")
                                st.image(response.content, caption=file_name)
                            elif 'application/pdf' in content_type:
                                st.success(f"Displaying PDF: {file_name}")
                                st.download_button("Download PDF", data=response.content, file_name=file_name, mime="application/pdf")
                            else:
                                st.success(f"Downloading {file_name}")
                                st.download_button("Download File", data=response.content, file_name=file_name, mime=content_type)
                        else:
                            st.error(f"Failed to retrieve file content: {response.text}")
                    else:
                        st.error(f"File not present in Cluster, CID: {cid}")
                except Exception as e:
                    st.error(f"Error: {e}")

# Streamlit Layout
upload_and_pin_file()
list_pinned_files()
unpin_file()
view_file_content()
perform_garbage_collection()

