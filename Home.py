import json

import streamlit as st
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_community.retrievers.wikipedia import WikipediaRetriever
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

from function_calling import CreateQuiz
from session import Session

st.set_page_config(
    page_title='Quiz GPT',
    page_icon='🧐'
)

st.title('Quiz GPT')


@st.cache_data(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = f"./.cache/quiz_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    return docs


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a helpful assistant that is role playing as a teacher.

    Based ONLY on the following context make 10 questions to test the user's knowledge about the text.
    
    Each question should have 4 answers, three of them must be incorrect and one should be correct.
         
    Use (o) to signal the correct answer.
         
    Question examples:
         
    Question: What is the color of the ocean?
    Answers: Red|Yellow|Green|Blue(o)
         
    Question: What is the capital or Georgia?
    Answers: Baku|Tbilisi(o)|Manila|Beirut
         
    Question: When was Avatar released?
    Answers: 2007|2001|2009(o)|1998
         
    Question: Who was Julius Caesar?
    Answers: A Roman Emperor(o)|Painter|Actor|Model
         
    Your turn!
    
    Context: {context}
    """,
        )
    ]
)

quiz_source = Session(name='quiz_source')
grade = Session(name='grade')
api_key = Session(name='api_key')


@st.cache_data(show_spinner="Making_quiz...")
def run_quiz_chain(_docs, topic):
    chain = {"context": format_docs} | prompt | llm_with_functions
    return chain.invoke(_docs)


@st.cache_data(show_spinner="Searching Wikipedia...")
def wiki_search(term):
    retriever = WikipediaRetriever(top_k_results=5)
    return retriever.get_relevant_documents(topic)


with st.sidebar:
    docs = None
    api_key_input = st.text_input('OPENAI_API_KEY', placeholder='Enter OpenAI API Key')
    if api_key_input:
        api_key.state = api_key_input
    choice = st.selectbox(
        "Choose what you want to use.",
        (
            "File",
            "Wikipedia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file)

    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            docs = wiki_search(topic)

if api_key.value:
    try:
        llm = ChatOpenAI(
            openai_api_key=api_key.value,
            temperature=0.1,
            model="gpt-3.5-turbo-1106",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
        tools = [CreateQuiz]
        functions = [convert_to_openai_tool(t) for t in tools]
        llm_with_functions = llm.bind_functions(tools)

        if st.button("Generate Quiz"):
            quiz_source.state = run_quiz_chain(docs, topic if topic else file.name)

        if quiz_source.value:
            result_json = quiz_source.value.additional_kwargs["function_call"]["arguments"]
            result_dict = json.loads(result_json)
            # print(type(result_dict))
            grades = []
            with st.form("questions_form"):
                for idx, question in enumerate(result_dict["questions"]):
                    st.write(question["question"])
                    value = st.radio(
                        "Select an option.",
                        [answer["answer"] for answer in question["answers"]],
                        index=None,
                        key=f'answer_{idx}'
                    )
                    if {"answer": value, "correct": True} in question["answers"]:
                        st.success("Correct!")
                        grades.append(1)
                    elif value is not None:
                        grades.append(0)
                        st.error("Wrong!")
                button = st.form_submit_button()
                grade.state = sum(grades)

        if grade.value == 10:
            st.balloons()
    except:
        st.write('OPENAI API KEY 를 입력하세요')