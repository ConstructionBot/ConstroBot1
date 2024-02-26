import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from pandasai import SmartDatalake
from pandasai.llm.openai import OpenAI
from pandasai.middlewares import StreamlitMiddleware
from pandasai.responses.streamlit_response import StreamlitResponse

# Loading Environment Variables Using the `dotenv` Package
load_dotenv()

# Function to load OpenAI API key
def load_openai_api_key():
    # Check if OPENAI_API_KEY is set in environment variables
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    # Check if secrets.toml file exists and contains OPENAI_API_KEY
    elif os.path.exists("secrets.toml"):
        secrets = st.secrets()
        if "OPENAI_API_KEY" in secrets:
            return secrets["OPENAI_API_KEY"]
    return None

if __name__ == "__main__":
    st.set_page_config(
        layout="wide",
        page_icon="./image/logo.svg",
        page_title="Construction chatbot",
    )
    st.title("Chatbot for Contracts Management")
    st.text("Chatbot for Contracts Management is a data analysis app powered by LLM, that will help u making your construction work easier.Owned By Ashish Sonawane"
        )
    st.markdown("""List of todos before uploading Excel sheet
     - [ ] First Row of Excel Sheet must be the colomn names
     - [ ] If there is main heading and then subheading ,Remove main heading
     - [ ] While asking Question Colomn names must be accurate 
     """)
    # Sidebar for API Key settings
    with st.sidebar:
        st.header(
            "Set your API Key",
            help="You can get it from [OpenAI](https://platform.openai.com/account/api-keys/), or buy it conveniently from [here](https://api.nextweb.fun/).",
        )

        # Get OpenAI API key
        openai_api_key = st.text_input(
            "Enter API Key",
            type="password",
            value=load_openai_api_key(),
        )

        # Create OpenAI instance
        llm = OpenAI(api_token=openai_api_key)

    # Main content area
    with st.container():
        # Allow user to upload multiple files
        input_files = st.file_uploader(
            "Upload files", type=["xlsx", "csv"], accept_multiple_files=True
        )

        # If user uploaded files, load them
        if input_files:
            data_list = []
            for input_file in input_files:
                if input_file.name.lower().endswith(".csv"):
                    # Read CSV file with delimiter and handle parsing errors
                    try:
                        data = pd.read_csv(input_file, error_bad_lines=False)
                    except pd.errors.ParserError as e:
                        st.error(f"Error parsing CSV file: {e}")
                        continue  # Skip to the next file if parsing fails
                else:
                    data = pd.read_excel(input_file)
                st.dataframe(data, use_container_width=True)
                data_list.append(data)
        # Otherwise, load the default file
        else:
            st.header("Example Data")
            data = pd.read_excel("./Sample.xlsx")
            st.dataframe(data, use_container_width=True)
            data_list = [data]

        # Create SmartDatalake instance
        df = SmartDatalake(
            dfs=data_list,
            config={
                "llm": llm,
                "verbose": True,
                "response_parser": StreamlitResponse,
                "middlewares": [StreamlitMiddleware()],
            },
        )

        # Input text
        st.header("Ask anything!")
        input_text = st.text_area(
            "Enter your question", value="Firstly read all the data by yourself from the file?"
        )

        if input_text:
            if st.button("Start Execution"):
                result = df.chat(input_text)

                # Display the result and code in two columns
                col1, col2 = st.columns(2)

                with col1:
                    # Display the result
                    st.header("Answer")
                    st.write(result)
