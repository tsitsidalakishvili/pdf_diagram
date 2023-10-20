import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.chains import GraphCypherQAChain
from langchain.graphs import Neo4jGraph
from langchain.document_loaders import PyPDFLoader
import openai
import re
import constants

# Set Streamlit App title
st.title("PDF to Neo4j Graph Converter")

PDF_PATH = "./3_oil_and_gas_separation_design_manual_by_c_richard_sivalls.pdf"

# Create a PDF loader
loader = PyPDFLoader(PDF_PATH, extract_images=True)

# Load and process the uploaded PDF file
pages = loader.load()

# Display the content of the first page if it exists
if pages:
    page_content = pages[0].page_content
    st.subheader("Page Content:")
    st.write(page_content)
else:
    st.error("No pages found.")

# Set your OpenAI API key
openai.api_key = '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'

# Extract data model suggestion
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=f"Suggest graph data model based on elements extracted from PDF drawings in input_data: {page_content}",
    max_tokens=500,
)

suggested_data_model = response.choices[0].text.strip()
st.subheader("Suggested Data Model:")
st.markdown(f"**{suggested_data_model}**")

# Get Cypher Query
conversation = [
    {"role": "system", "content": "You are a helpful assistant. You are skilled in Neo4j(data models), Python, and Langchain."},
    {"role": "user", "content": f"Generate a Neo4j Cypher query to create nodes and relationships, properties, and labels based on the following suggested data model: {suggested_data_model}"}
]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=conversation,
    max_tokens=1000,
)

# Extract Cypher Query
suggested_cypher_query = response.choices[0].message["content"]
match = re.search(r'```(.*?)```', suggested_cypher_query, re.DOTALL)
if match:
    actual_cypher_query = match.group(1).strip()
    st.subheader("Suggested Cypher Query:")
    st.code(actual_cypher_query)
else:
    st.error("No valid Cypher query detected in the response.")

# Neo4j Connection Details
st.subheader("Neo4j Connection Details:")
url = st.text_input("URL", "bolt://44.210.127.96:7687")
username = st.text_input("Username", "neo4j")
password = st.text_input("Password", "chairwoman-calculations-tops", type="password")
connect_button = st.button("Connect and Execute Query")

if connect_button:
    graph = Neo4jGraph(url=url, username=username, password=password)
    try:
        graph.query(actual_cypher_query)
        st.success("Query executed successfully!")
    except Exception as e:
        st.error(f"Error executing the query: {e}")
