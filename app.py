import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.title("Chat with SQL DB")

INJECTION_WARNING = """
    SQL 
"""
localDB = "use_localDB"
mySQL = "use_mySQL"

radio_opt = ["Use SQLLite3 database", "Connect to your own database"]

selected_opt = st.sidebar.radio(label = "Choose your database", options = radio_opt)

if radio_opt.index(selected_opt) ==1:
    db_uri = mySQL
    mySQL_host = st.sidebar.text_input("Provide the SQL host")
    mySQL_user = st.sidebar.text_input("Provide the SQL username")
    mySQL_password = st.sidebar.text_input("Provide the password",type= "password")
    mySQL_db = st.sidebar.text_input("mySQL database")

else:
    db_uri = localDB
api_key = st.sidebar.text_input(label = "GROQ API key", type = "password")

if not db_uri:
    st.info("Please enter database information and uri")

if not api_key:
    st.info("Please enter GROQ API key")

llm = ChatGroq(groq_api_key = api_key,model_name="llama3-70b-8192",streaming=True)
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mySQL_host=None,mySQL_user=None,mySQL_password=None,mySQL_db=None ):
    if db_uri == localDB:
        filepath = (Path(__file__).parent/"Products.db").absolute()
        print(filepath)
        creator = lambda: sqlite3.connect(f"file:{filepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator= creator))
    
    elif db_uri == mySQL:
        if not (mySQL_db or mySQL_user or mySQL_password or mySQL_host):
            st.error('Please provide all connection details.')
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mySQL_user}:{mySQL_password}@{mySQL_host}/{mySQL_db}"))

if db_uri == mySQL:
    db = configure_db(db_uri, mySQL_host,mySQL_user,mySQL_password,mySQL_db)
else:
    db = configure_db(db_uri) 

toolkit = SQLDatabaseToolkit(db = db, llm = llm)

agent = create_sql_agent(
    llm = llm,
    toolkit = toolkit,
    verbose = True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content":"How can i help you"}]

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

user_query = st.chat_input(placeholder = "Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query,callbacks = [streamlit_callback])
        st.session_state.messages.append({"role":"assistant", "content":response})
        st.write(response)