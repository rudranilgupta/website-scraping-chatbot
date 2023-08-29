import logging
import openai
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import pinecone
import os
from langchain.embeddings.openai import OpenAIEmbeddings

_ = load_dotenv(find_dotenv())  # read local .env file

# Logging configuration
logging.basicConfig(filename='app.log', level=logging.INFO)

####### Initializing the openai and pinecone #######
openai.api_key = os.getenv('OPENAI_API_KEY')
# find API key in console at app.pinecone.io
YOUR_API_KEY = os.getenv("PINECONE_API_KEY")
# find ENV (cloud region) next to API key in console
YOUR_ENV = os.getenv("PINECONE_ENVIRONMENT")

pinecone.init(api_key=YOUR_API_KEY, environment=YOUR_ENV)

    # Initialize OpenAI Embeddings
embed = OpenAIEmbeddings(
        model='text-embedding-ada-002',
        openai_api_key=os.getenv('OPENAI_API_KEY')
)

def replying(question):
        '''
        This function is taking questions asked by user as input, converting it into embeddings,
        performing cosine similarity search with the embeddings of the documents and returning the reply
        along with the source details of the query asked.
        '''
        index = pinecone.Index('rudranil')
        text_field = 'text'
        namespace = 'rudra'

        query = question
        vectorstore = Pinecone(
            index, embed.embed_query, text_field, namespace
        )
        vectorstore.similarity_search(
            query,  # our search query
            k=3  # return 3 most relevant docs
        )

        # completion llm
        llm = ChatOpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model_name='gpt-3.5-turbo',
            temperature=0.0
        )

        qa_with_sources = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever()
        )
        reply = qa_with_sources(query)
        return reply['result']

#print(replying('Tell me something about Sherlock Holmes'))