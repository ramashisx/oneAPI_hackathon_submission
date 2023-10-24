import streamlit as st
import requests


URL = "http://127.0.0.1:4444/"


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
    top_image_bar.image("../assets/top_image.jpg", width=256)

    # Display the app title
    st.title("Intel OneAPI")

    # Create a form to collect the context and question from the user
    with st.form("form"):
        context = st.text_area("Enter Context", placeholder="Enter the context for your question here...", height=200)
        question = st.text_input("Enter Question", placeholder="Enter your question here...")

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
