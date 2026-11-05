import streamlit as st
from workflow import fetch_code_node, code_fixer_node, submit_pr_node

st.set_page_config(page_title="AI Open-Source PR Bot", page_icon="🐙", layout="wide")

st.title("🐙 AI GitHub Open-Source PR Contributor")
st.caption("Auto-analyze repo code, generate fixes, and submit REAL Pull Requests with Human-in-the-Loop Approval!")

# Sidebar Setup
st.sidebar.title("📌 Target Repository Setup")
repo_name = st.sidebar.text_input("GitHub Repo (username/repo):", value="octocat/Hello-World")
filepath = st.sidebar.text_input("File Path in Repo:", value="README")
issue_desc = st.sidebar.text_area("Issue / Bug Description:", value="Update documentation with modern guidelines and formatting.")

if "pr_stage" not in st.session_state:
    st.session_state.pr_stage = "IDLE"
if "pr_state" not in st.session_state:
    st.session_state.pr_state = {}

# Step 1: Fetch Code and Propose Fix
if st.sidebar.button("🔍 Fetch Code & Generate Fix", type="primary", use_container_width=True):
    with st.spinner("🤖 Agent fetching code from GitHub & generating fix..."):
        initial_state = {
            "repo_name": repo_name,
            "filepath": filepath,
            "issue_description": issue_desc,
            "original_code": "",
            "fixed_code": "",
            "pr_title": "",
            "pr_body": "",
            "status_msg": ""
        }
        
        s1 = fetch_code_node(initial_state)
        initial_state.update(s1)
        
        if "Error" in initial_state["status_msg"]:
            st.error(initial_state["status_msg"])
        else:
            s2 = code_fixer_node(initial_state)
            initial_state.update(s2)
            st.session_state.pr_state = initial_state
            st.session_state.pr_stage = "REVIEW_READY"

st.divider()

# Step 2: Human-in-the-Loop Approval UI
if st.session_state.pr_stage == "REVIEW_READY":
    state = st.session_state.pr_state
    
    st.subheader("🛑 Human Approval Required Before Submitting PR")
    st.info("Review the AI-generated code diff below. Click **Approve & Submit Real PR** to trigger GitHub API!")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### 📄 Original Code from Repo:")
        st.code(state["original_code"], language="python")
    with col_b:
        st.write("### ✨ AI Proposed Fixed Code:")
        edited_fixed_code = st.text_area("You can edit the code before approving:", value=state["fixed_code"], height=300)
    
    st.divider()
    
    btn1, btn2, _ = st.columns([1, 1, 2])
    with btn1:
        if st.button("🚀 Approve & Submit Real PR", type="primary", use_container_width=True):
            state["fixed_code"] = edited_fixed_code
            with st.spinner("⚡ Creating branch and opening Pull Request on GitHub..."):
                final_res = submit_pr_node(state)
                st.session_state.pr_stage = "DONE"
               # st.session_state.final_msg = final_res["status_message"]
                st.session_state.final_msg = final_res["status_msg"]
                st.rerun()

    with btn2:
        if st.button("❌ Cancel / Reject", type="secondary", use_container_width=True):
            st.session_state.pr_stage = "IDLE"
            st.warning("Action cancelled. No PR was submitted.")
            st.rerun()

if st.session_state.pr_stage == "DONE":
    st.markdown(st.session_state.final_msg)