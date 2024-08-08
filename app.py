import streamlit as st
from sqlalchemy.orm import scoped_session
from db import init_db, get_session
from model import User, Document, UserHistory
from utils import process_document

# Initialize the database
init_db()

# Create a scoped session
session = scoped_session(get_session)

def main():
    st.title("Document Query Application")

    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['username'] is None:
        menu = ["Home", "Login", "SignUp"]
    else:
        menu = ["Home", "Upload Document", "Query Document", "History", "Download History", "Logout"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        if st.session_state['username']:
            st.subheader(f"Hi {st.session_state['username']}, welcome!")
        else:
            st.subheader("Home")
            st.write("Please login or sign up to continue.")

    if choice == "Login":
        if st.session_state['username'] is None:
            username = st.text_input("Username")
            password = st.text_input("Password", type='password')
            if st.button("Login"):
                user = session.query(User).filter_by(username=username).first()
                if user and user.verify_password(password):
                    st.success(f"Logged in as {username}")
                    st.session_state["username"] = username
                else:
                    st.error("Invalid username or password")
        else:
            st.write("You are already logged in.")

    if choice == "SignUp":
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            user = User(username=username)
            user.password = password
            session.add(user)
            session.commit()
            st.success("You have successfully created an account")

    if choice == "Upload Document":
        if st.session_state['username'] is not None:
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
            if st.button("Upload"):
                if uploaded_file is not None:
                    user = session.query(User).filter_by(username=st.session_state['username']).first()
                    content = process_document(uploaded_file)
                    document = Document(filename=uploaded_file.name, text=content, user_id=user.id)
                    session.add(document)
                    session.commit()
                    st.success("Document uploaded successfully")
                else:
                    st.error("Please select a file to upload.")
        else:
            st.error("Please login first.")

    if choice == "Query Document":
        if st.session_state['username'] is not None:
            st.subheader("Query Document")
            query = st.text_input("Enter your query")
            if st.button("Search"):
                user = session.query(User).filter_by(username=st.session_state['username']).first()
                documents = session.query(Document).filter(Document.user_id == user.id, Document.text.contains(query)).all()
                if documents:
                    for doc in documents:
                        st.write(f"Document: {doc.filename}")
                        st.write(doc.text)
                    for doc in documents:
                        user_history = UserHistory(user_id=user.id, query=query, response=doc.text)
                        session.add(user_history)
                    session.commit()
                else:
                    st.write("No documents found")
        else:
            st.error("Please login first.")

    if choice == "History":
        if st.session_state['username'] is not None:
            st.subheader("User History")
            if st.button("Get History"):
                user = session.query(User).filter_by(username=st.session_state['username']).first()
                history = session.query(UserHistory).filter_by(user_id=user.id).all()
                if history:
                    for record in history:
                        st.write(f"Query: {record.query}")
                        st.write(f"Response: {record.response}")
                else:
                    st.write("No history found")
        else:
            st.error("Please login first.")

    if choice == "Download History":
        if st.session_state['username'] is not None:
            st.subheader("Download History")
            if st.button("Download"):
                user = session.query(User).filter_by(username=st.session_state['username']).first()
                history = session.query(UserHistory).filter_by(user_id=user.id).all()
                if history:
                    formatted_history = "\n".join([f"{record.query} -> {record.response}" for record in history])
                    st.download_button(label="Download History", data=formatted_history, file_name=f"{user.username}_history.txt")
                else:
                    st.write("No history found")
        else:
            st.error("Please login first.")

    if choice == "Logout":
        st.session_state['username'] = None
        st.success("Logged out successfully")

if __name__ == '__main__':
    main()
