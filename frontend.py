from dotenv import load_dotenv, find_dotenv
import openai
import os
import streamlit as st
import csv
from datetime import datetime
import logging
import scrape
import pinecone_qa, answers

_ = load_dotenv(find_dotenv())  # read local .env file

openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure logging format and level
logging.basicConfig(
    filename='red_bot.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

st.set_page_config(page_title="VERCEL_BOT")


def main():

    # Set app title and information button
    st.title("Website Scraping Chatbot")
    col1, col2 = st.columns([2, 2])

    # Initialize conversation history
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    # Initialize send button state
    if 'send_button_pressed' not in st.session_state:
        st.session_state.send_button_pressed = False

    # User input: Website
    with col2:
        website = st.text_input("Website address", key="user_input1", value="", help="Enter website address...")
        if st.button("Crawl"):
            if website:
                try:
                    content = scrape.web_scrape(website)
                    pinecone_qa.vectors(website, content)
                    st.text_area(label ="",value=content, height=300,disabled=True)
                    
                except Exception as e:
                    logging.error("An error occurred while processing the request.")
                    logging.error(e)
                    st.error("An error occurred while processing the request. Please try again.")
                else:
                    st.session_state.send_button_pressed = False

    with col1:
        # User input: Question
        question = st.text_input("User Input", key="user_input2", value="", help="Enter your message...",disabled=(website == ""))

        if st.button("Send") or st.session_state.send_button_pressed:
            st.session_state.send_button_pressed = True
            if question:
                try:
                    # Load transcripts

                    reply = answers.replying(question)

                    # Store conversation history
                    st.session_state.conversation.append((question, reply))

                    # Save conversation in a CSV file
                    save_conversation(question, reply)

                    display_conversation()
                except Exception as e:
                    logging.error("An error occurred while processing the request.")
                    logging.error(e)
                    st.error("An error occurred while processing the request. Please try again.")
                else:
                    st.session_state.send_button_pressed = False




def save_conversation(question, answer):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    headers = ["Time", "Question Asked", "Answer"]

    with open('conversation.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        # Write headers if the file is empty
        if file.tell() == 0:
            writer.writerow(headers)
        writer.writerow([timestamp, question, answer])


def display_message(text, sender):

    if sender == "user":
        st.write(":man: " + text)
    else:
        st.write(":robot_face: " + text)


def display_conversation():

    st.subheader("Conversation History")
    for question, reply in st.session_state.conversation:
        display_message(question, "user")
        display_message(reply, "bot")

# Run the app
if __name__ == "__main__":
    main()