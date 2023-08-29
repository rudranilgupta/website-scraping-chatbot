import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from uuid import uuid4
from dotenv import load_dotenv, find_dotenv
import pinecone, os
from langchain.embeddings.openai import OpenAIEmbeddings

_ = load_dotenv(find_dotenv())  # read local .env file

####### Initializing the openai and pinecone #######
openai.api_key = os.getenv('OPENAI_API_KEY')
# find API key in console at app.pinecone.io
YOUR_API_KEY = os.getenv("PINECONE_API_KEY")
# find ENV (cloud region) next to API key in console
YOUR_ENV = os.getenv("PINECONE_ENVIRONMENT")

# Initialize Pinecone
pinecone.init(api_key=YOUR_API_KEY, environment=YOUR_ENV)

# Initialize OpenAI Embeddings
embed = OpenAIEmbeddings(
    model='text-embedding-ada-002',
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

####### Required Variables #######
def vectors(web_url,content):
    texts = []
    VectorStore = []
    records = []

    # Initialize Pinecone Index
    index = pinecone.Index('rudranil')
    ## Splitting the complete paragraphs in relevant chunks of size 1200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        length_function=len,
    )

    try:
        texts.append(text_splitter.split_text(content))
        logging.info(f"Texts: {texts}")
        ## now we are creating embeddings for the above text chunks for each file
        for i in range(len(texts)):
            VectorStore.append(openai.Embedding.create(
                input=texts[i],
                engine="text-embedding-ada-002"
            ))

        ## running a for loop to create a list of tuples having (id, vector embeddings, metadata) as values.
        ## metadata contains the chunk_id, text of the chunk, a string containing information of the video name and the link
        for i, l in zip(VectorStore, range(len(texts))):
            k = len(i.data)
            cnt = 0
            zoa = texts[l]
            rh = 0
            for j in range(k):
                metadata = {'chunk_id': j, 'text': zoa[rh], 'url': web_url}
                r = [str(uuid4()), i['data'][j]['embedding'], metadata]
                record = tuple(r)
                records.append(record)
                rh += 1
            cnt += 1

        ## inserting the above created list into Pinecone index 'redbot'
        index.upsert(vectors=records, namespace='rudra')

    except Exception as e:
        logging.error("An error occurred: " + str(e))

