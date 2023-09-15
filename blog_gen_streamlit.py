import streamlit as st
import time
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from PIL import Image
from io import BytesIO

OPENAI_API_KEY = st.secrets.OPENAI_API_KEY

llm = ChatOpenAI(temperature=0.9, openai_api_key = OPENAI_API_KEY)

# Function to generate the blog (You'll need to implement this)
def generate_blog(description, language, theme, customization_options, code_snippets, videos):
    prompt = "Create a {theme} blog on {description} in {words} words. It should be written in {language}."
        
    tone = customization_options['tone'] 

    if len(tone)>0:
        prompt = prompt + "The style/tone of the blog should be in " + tone + "style. " 

    if len(code_snippets)>0:
        prompt = prompt + "Also include code samples in blog, here are the samples you will use: " + '\n'.join(code_snippets)

    if len(videos)>0:
        prompt = prompt + "Also include these videos by saying, here are videos on the topic for reference " + '\n'.join(videos)
    
    nwords = customization_options['words']

    if customization_options['Generate Code Snippets'] == "Yes":
        prompt = prompt + "You will generate and include code relevant to the topic at relevant intervals, keep the code snippets brief"

    prompt = ChatPromptTemplate.from_template(
        prompt
    )

    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run(theme = theme, description = description, words = nwords, language = language)

    # st.success("Blog Generation Complete!")
    # st.progress(100)
    # pass

def enhance_blog(user_blog, prompt):
    pass


def get_image_from_api(text):
    # Replace with your API function call
    import requests

    API_URL = "https://api-inference.huggingface.co/models/jayavibhav/trial-jv"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.content
    image_bytes = query({
        "inputs": "{}".format(text),
    })

    return image_bytes

# Streamlit App

def main():
    # Set the background color to grey
    st.set_page_config(
        page_title="Blog Generator by tl;dwr",
        page_icon="✍️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Blog Generator!")

    # Input for language selection
    language = st.selectbox("Select Language:", ["English", "Spanish", "French", "Other"])
    if language == "Other":
        custom_theme = st.text_input("Enter Language:")
        theme = custom_theme if custom_theme else language
    # Input for blog description
    description = st.text_area("Enter Blog Description:")

    # Dropdown for themes selection, including "Other" option
    theme_options = ["Technology", "Science", "Education", "Other"]
    theme = st.selectbox("Select Blog Theme:", theme_options)
    
    # If the user selects "Other," allow them to enter a custom theme
    if theme == "Other":
        custom_theme = st.text_input("Enter Custom Theme:")
        theme = custom_theme if custom_theme else theme

    images = st.radio("Generate Images using AI?", ["No", "Yes"])

    # Customization options (checkboxes, sliders, etc.)
    st.sidebar.title("Customization Options")
    
    customization_options = {
        "words": st.sidebar.slider("Number of words", 0, 1000, 250),
        "tone": st.sidebar.text_input("Additional inputs (Tone, Writing Style)"),
        "Generate Code Snippets": st.sidebar.radio("Generate Code Snippets?", ["No", "Yes"]),
        "Add custom Code Snippets": st.sidebar.radio("Add custom Code Snippets?", ["No", "Yes"]),
        "Include Videos": st.sidebar.radio("Include Videos?", ["No", "Yes"]),
    }

    # Input for code snippets (visible when "Yes" is selected)
    if customization_options["Add custom Code Snippets"] == "Yes":
        code_snippets = st.text_area("Add Code Snippets (separate with a delimiter, e.g., '//'):")

    # Input for videos (visible when "Yes" is selected)
    if customization_options["Include Videos"] == "Yes":
        videos = st.text_area("Add Videos (separate with a delimiter, e.g., ';'):")

    # Create Blog Button
    if st.button("Create Blog!"):
        if description:
            with st.spinner("Generating Blog..."):
            # Split code snippets, videos, and images into lists
                code_snippets = code_snippets.split('//') if customization_options["Add custom Code Snippets"] == "Yes" else []
                videos = videos.split(';') if customization_options["Include Videos"] == "Yes" else []

                # Call the generate_blog function with user inputs
                generated_blog = generate_blog(description, language, theme, customization_options, code_snippets, videos)
                
                # Allow users to edit the generated content
                st.subheader("Generated Blog (Editable):")
                user_edited_blog = st.text_area("Edit the Blog Content:", value=generated_blog, height = 400)

                if images == "Yes":
                    
                    progress_bar = st.progress(0)
                    time.sleep(0.5)
                    with st.empty():
                        for i in range(86):
                            progress_bar.progress(i)
                            time.sleep(0.10)

                    prompt = ChatPromptTemplate.from_template("Give me an image generation prompt for {blog}")

                    chain = LLMChain(llm=llm, prompt=prompt)

                    img_prompt = chain.run(generated_blog)

                    image_bytes = get_image_from_api(img_prompt)

                    if image_bytes:
                        image = Image.open(BytesIO(image_bytes))
                        st.image(image, caption="Generated Image", use_column_width=True)

                        progress_bar.progress(100)

                    else:
                        st.warning("No image received from the API.")
                    
                    
                # choice = st.radio('Enhance blog?', ["No", "Yes"])

                # if choice == "Yes":
                #     enhance = st.text_input("Enter a manual prompt to enhance the blog:")

                #     prompt = ChatPromptTemplate.from_template("Enhance the {blog} by considering {enhance}")

                #     chain = LLMChain(llm=llm, prompt=prompt)

                #     out = chain.run(user_edited_blog, enhance)

                #     final_output = st.text_area("Here's your final blog:", value = out)                    
                st.markdown('Not decided on which platform to upload your blog? \n Try out [Blogify]("https://blogify-ai.netlify.app/")')

        else:
            st.warning("Please enter a blog description.")

if __name__ == "__main__":
    main()
