import streamlit as st
import requests


URL = "http://localhost:4444/"


def main():
    """Main function of the Streamlit app."""

    # Set the page configuration
    st.set_page_config(layout="wide", page_title="OneAPI", page_icon="🤖")

    # Add a custom CSS theme
    with open("./ui/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Create a container for the top image bar
    top_image_bar = st.container()

    # Add an image to the top image bar
    top_image_bar.image("./ui/top_image.jpg", width=256)

    # Display the app title
    st.title("Intel OneAPI")

    input_choice = st.radio("Choose an input method", ["Enter Text", "Upload a File"])

    # Create a form to collect the context, question, and file or text choice from the user
    with st.form("form"):
        
        context = ""
        question = ""
        uploaded_file = None

        if input_choice == "Enter Text":
            value = """Joey felt the very first rain drop hit his hat. 

"Let's go inside!" he said to his friend Billy. 

The two ran inside the house as it began to rain more outside. Joey's mother was very happy that they missed the rain and got inside before it made a big mess. Joey and Billy weren't as happy. 

"What are we going to do in here all day?" asked Billy. 

"I don't know" said Joey, looking out the window as the rain came down. 

Harder. And harder. 

"Oh no! I left my baseball glove outside" said Joey as he watched it begin to fill up with rain. His glove was going to be a mess! 

Thankfully, Joey's dad pulled up in his car. Seeing the glove on the ground, he picked it up as he ran inside. 

"Careful sport, you almost lost this" he told his son as he tossed him the wet mitt. But Joey wasn't listening, he was looking past his dad as he walked through the door. The sky was clearing up! Joey ran outside, Billy came after him. 

"Look at that!" Billy said as he pointed at the sky. A rainbow was appearing, it was so beautiful! The rain wasn't bad after all!"""
            
            context = st.text_area("Enter Context", placeholder="Enter the context for your question here...", value=value, height=200)
        else:
            uploaded_file = st.file_uploader("Upload a File", type=["txt"])
            if uploaded_file:
                context = uploaded_file.read().decode('utf-8')

        value = "What was he doing at the time?"
        question = st.text_input("Enter Question", placeholder="Enter your question here.", value=value)
        submit_button = st.form_submit_button("Submit")

    # If the user has submitted the form, submit the context and question to the Bard AI service
    if submit_button:
        payload = {
            "context": context,
            "question": question
        }

        answer = requests.post(URL, json=payload)

        if answer.status_code == 200:
            answer = eval(answer.content)["answer"]
            
            # Write the answer as a title
            st.markdown(f"""
                        <div class="answer_heading">
                        Answer
                        </div>
                        """, unsafe_allow_html=True)

            # Write the answer
            st.markdown(f"""
                        <div class="answer">
                        {answer}
                        </div>
                        """, unsafe_allow_html=True)

        else:
            # Something went wrong with the request
            st.error("Something went wrong while fetching the answer. Please try again later.")

    # Add a footer with some information
    st.sidebar.markdown(
        """
        *Built with ❤️ by Ramashish using Intel OneAPI*

        **Source code**: [GitHub](https://github.com/ramashisx/oneAPI_hackathon_submission)
        """
    )

if __name__ == "__main__":
    main()
