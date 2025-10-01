# app.py
import streamlit as st
import pandas as pd
from agent.agent import run_agent  # Your agent function
from fpdf import FPDF
import io
import tempfile

# Load CSV data once
@st.cache_data
def load_data():
    actuals = pd.read_csv("fixtures/data.csv")
    budget = pd.read_csv("fixtures/budget.csv")
    fx = pd.read_csv("fixtures/fx.csv")
    cash = pd.read_csv("fixtures/cash.csv")
    return actuals, budget, fx, cash

actuals, budget, fx, cash = load_data()

st.set_page_config(page_title="CFO Copilot", layout="wide")
st.title("CFO Copilot 💼")

# Input box
question = st.text_input("Ask a finance question:", "")

if question:
    # Run agent
    response_text, fig = run_agent(question, actuals, budget, fx, cash)
    
    # Show text
    st.markdown(f"**Answer:** {response_text}")
    
    # Show chart if exists
    if fig is not None:
        st.pyplot(fig)
        # Export PDF button
    if st.button("Export PDF"):
        # Save matplotlib figure to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name, format="png")
            tmpfile_path = tmpfile.name

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.multi_cell(0, 10, f"CFO Copilot Report\nQuestion: {question}\n\n", align='C')
        pdf.image(tmpfile_path, x=15, y=40, w=180)  # Insert chart
        pdf_output = f"CFO_Report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(pdf_output)

        st.success(f"PDF exported as {pdf_output}")
        st.download_button("Download PDF", data=open(pdf_output, "rb"), file_name=pdf_output)
