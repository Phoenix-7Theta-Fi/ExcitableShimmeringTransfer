import streamlit as st
import requests
from PIL import Image
import io
import google.generativeai as genai
from notion_client import Client

# Initialize APIs (you'll need to replace these with your actual API keys)
notion = Client(auth="your_notion_api_key")
genai.configure(api_key="your_gemini_api_key")

def analyze_image(image):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content(["Analyze this handwritten note and provide a summary", image])
    return response.text

def analyze_text(text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Summarize and analyze the following note: {text}")
    return response.text

def get_notion_pages(database_id):
    pages = notion.databases.query(database_id=database_id).get("results")
    return pages

def summarize_notion_content(pages):
    content = "\n".join([page["properties"]["Content"]["rich_text"][0]["text"]["content"] for page in pages if page["properties"]["Content"]["rich_text"]])
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"Summarize the following Notion content:\n{content}")
    return response.text

def suggest_integration(new_content, existing_summary):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    New content:
    {new_content}

    Existing Notion summary:
    {existing_summary}

    Based on the new content and the existing Notion summary, suggest how to integrate the new content into the user's Notion workspace. Provide specific recommendations on where to place the new information and how it relates to existing content.
    """
    response = model.generate_content(prompt)
    return response.text

def provide_insights(new_content, existing_summary):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    New content:
    {new_content}

    Existing Notion summary:
    {existing_summary}

    Analyze the new content in conjunction with the existing Notion summary. Provide insights, identify patterns, suggest potential action items, and highlight any important connections or contradictions between the new and existing information.
    """
    response = model.generate_content(prompt)
    return response.text

def update_notion(title, content, database_id):
    notion.pages.create(
        parent={"database_id": database_id},
        properties={
            "Title": {"title": [{"text": {"content": title}}]},
            "Content": {"rich_text": [{"text": {"content": content}}]}
        }
    )

def main():
    st.title("Advanced Creative Note-Taking App")

    # Notion database selection
    database_id = st.text_input("Enter your Notion database ID")

    if not database_id:
        st.warning("Please enter a Notion database ID to proceed.")
        return

    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["Image Upload", "Text Input"])

    with tab1:
        st.header("Upload Handwritten Note")
        uploaded_file = st.file_uploader("Upload a photo of your handwritten note", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            if st.button("Analyze Image"):
                with st.spinner("Analyzing image..."):
                    new_content = analyze_image(image)
                    st.write("Image Analysis:", new_content)
                    process_new_content(new_content, "Handwritten Note", database_id)

    with tab2:
        st.header("Type Your Note")
        note_title = st.text_input("Note Title")
        note_content = st.text_area("Note Content", height=200)

        if st.button("Analyze Text"):
            if note_title and note_content:
                with st.spinner("Analyzing text..."):
                    new_content = analyze_text(note_content)
                    st.write("Text Analysis:", new_content)
                    process_new_content(new_content, note_title, database_id)
            else:
                st.warning("Please enter both a title and content for your note.")

def process_new_content(new_content, title, database_id):
    with st.spinner("Analyzing existing Notion content..."):
        pages = get_notion_pages(database_id)
        existing_summary = summarize_notion_content(pages)
        st.write("Existing Notion Summary:", existing_summary)

    with st.spinner("Generating integration suggestions..."):
        integration_suggestions = suggest_integration(new_content, existing_summary)
        st.write("Integration Suggestions:", integration_suggestions)

    with st.spinner("Providing insights..."):
        insights = provide_insights(new_content, existing_summary)
        st.write("Insights:", insights)

    if st.button("Save to Notion"):
        with st.spinner("Saving to Notion..."):
            update_notion(title, new_content, database_id)
            st.success("Note saved to Notion!")

if __name__ == "__main__":
    main()