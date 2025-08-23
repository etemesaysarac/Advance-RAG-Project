from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from openai import embeddings

load_dotenv()

urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

docs = [WebBaseLoader(url).load() for url in urls]
doct_list =[item for sublist in docs for item in sublist]

text_splitter = RecursiveCharacterTextSplitter().from_tiktoken_encoder(
    chunk_size=200, chunk_overlap =50)

siplits =text_splitter.split_documents(doct_list)

vectorstore = Chroma().from_documents(
    documents=siplits,
    collection_name="rag-chroma",
    embedding=OpenAIEmbeddings(),
    persist_directory="./.chroma"
)

retriver = Chroma(
    collection_name="rag-chroma",
    persist_directory="./.chroma",
    embedding_function=OpenAIEmbeddings(),).as_retriever()

if __name__ == '__main__':
    print(doct_list)