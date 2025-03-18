import streamlit as st
import pandas as pd
import json
from google import genai
from dotenv import load_dotenv, set_key
import os, time, re

# Load DataFrame (Replace 'linkedin_info.csv' with actual file path)
linkedinInfo = pd.read_csv('B2B-business-dataset-samples-main/LinkedIn-company-info.csv')

# Load JSON file containing industry-wise grouped data
with open("grouped_companies.json", "r") as f:
    industry_data = json.load(f)

# Configure Gemini API (Replace 'YOUR_GEMINI_API_KEY' with your API key)
load_dotenv()
api_key = os.environ.get('geminiApi')
client = genai.Client(api_key=api_key)

def clean_json_response(response_text):
    """Cleans API response text by removing unwanted characters before JSON parsing."""
    # Remove leading "json" text if present
    response_text = re.sub(r'^\s*json\s*', '', response_text, flags=re.IGNORECASE)

    # Remove triple quotes if present
    response_text = re.sub(r"'''|\"\"\"", "", response_text)

    # Strip extra spaces, newlines
    response_text = response_text.strip()

    return response_text

def get_company_info(company_name):
    """Retrieve company row from DataFrame"""
    company_row = linkedinInfo[linkedinInfo['name'].str.lower() == company_name.lower()]
    return company_row.iloc[0] if not company_row.empty else None

def get_competitor_analysis(company_name):
    """Send data to Gemini API and retrieve analysis."""
    company_info = get_company_info(company_name)
    if company_info is None:
        return {"error": "Company not found in dataset."}
    
    industry = company_info['industries']
    if industry not in industry_data:
        return {"error": "Industry data not available."}
    
    competitors_data = industry_data[industry]
    
    # Construct prompt

    json_structure = """{
    "competitor_1": {"name": "", "pros": "", "cons": ""},
    "competitor_2": {"name": "", "pros": "", "cons": ""},
    "competitor_3": {"name": "", "pros": "", "cons": ""}
}"""

    prompt = f"""
    You are an AI assistant specializing in business analysis and deep market research. Your task is to conduct a thorough competitive analysis of "{company_name}"
    Additionally, you must use the internet as much as possible to augment your findings, just like a PhD student with a new finding.

    **Company Details for "{company_name}":**
    - Specialities: {company_info['specialties']}
    - Location: {company_info['formatted_locations']}
    - Description: {company_info['description']}

    **Research Process:**

    1.  **Identify Top 3 Competitors:**
        * Analyze the provided JSON data (containing a list of companies in the same industry).
        * Compare specialities, locations, and descriptions to identify the 3 closest competitors to "{company_name}".
        * Provide a detailed justification for why each competitor was selected.
    2.  **Conduct In-Depth Competitor Analysis:**
        * For each competitor, analyze their strengths and weaknesses based on their descriptions and any publicly available information.
        * Where possible, infer customer sentiment and product reviews based on the available information, and clearly state those inferences. Ensure the 
        products you choose for sentiment analysis align with what {company_name} is offering currently. Perform a thorough analysis of {company_name}'s
        products and choose only those which have competing alternatives available in the market.
        * Research any publicly available information about each competitor to supplement the provided data.
        * For each competitor, provide details on their market positioning, and perceived customer value.
    3.  **Comparative Analysis:**
        * Compare "{company_name}" with its 3 closest competitors.
        * Identify the key competitive advantages of "{company_name}".
        * Identify the major shortcomings of the competitors' offerings.
        * Provide a summary of the competitive landscape.
    4.  **Report Findings:**
        * Present your findings in a structured JSON format as follows:
            {json_structure}
        * Include detailed explanations and justifications for your conclusions.
        * Be as comprehensive and thorough as possible in your analysis.
        * Ensure you have at least four pros and cons listed for each competitor. 
        * Research the competitors on the internet and find out additional information.
        * If possible, back your claims with real statistics sourced from the net.

    **Provided Company Data:**
    {json.dumps(competitors_data)}
    """
    
    # Call Gemini API
    response = client.models.generate_content(contents=prompt, model='gemini-2.0-flash')
    cleaned_response = clean_json_response(response.text)
    return cleaned_response

def format_competitor_analysis(competitors):
    """Formats competitor analysis into Streamlit's Markdown output."""

    competitor_keys = list(competitors.keys())
    competitor_names = [competitors[key]["name"] for key in competitor_keys]

    if "competitor_index" not in st.session_state:
        st.session_state.competitor_index = 0

    st.markdown("<h1 style='text-align: center; font-size: 36px;'>Competitor Analysis</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Competitor List</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'><b>{' | '.join(competitor_names)}</b></p>", unsafe_allow_html=True)

    current_competitor_key = competitor_keys[st.session_state.competitor_index]
    competitor = competitors[current_competitor_key]

    st.markdown(f"<h2 style='text-align: center; font-size: 30px; color: #007BFF;'>{competitor['name']}</h2>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: green; font-size: 24px;'>Pros</h3>", unsafe_allow_html=True)
    for pro in competitor["pros"]:
        st.markdown(f"<p style='font-size: 18px;'>✅ {pro}</p>", unsafe_allow_html=True)

    st.markdown("<h3 style='color: red; font-size: 24px;'>Cons</h3>", unsafe_allow_html=True)
    for con in competitor["cons"]:
        st.markdown(f"<p style='font-size: 18px;'>❌ {con}</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    #only decrement if not at the beginning.
    if st.session_state.competitor_index > 0:
        if col1.button("⬅️ Previous Competitor"):
            st.session_state.competitor_index -= 1

    if col2.button("Next Competitor ➡️", disabled=st.session_state.competitor_index == len(competitor_keys) - 1):
        st.session_state.competitor_index += 1

    st.markdown(
        """
        <style>
            .block-container {
                max-width: 800px;
                margin: auto;
                padding: 20px;
                background-color: #f9f9f9;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def export_to_csv(competitors):
    """Converts competitor data to a CSV-friendly format."""
    data = []
    for key, competitor in competitors.items():
        name = competitor.get("name", "Unknown")
        for pro in competitor.get("pros", []):
            data.append([name, "Pro", pro])
        for con in competitor.get("cons", []):
            data.append([name, "Con", con])

    df = pd.DataFrame(data, columns=["Company", "Type", "Description"])
    return df


# Streamlit UI
st.title("Company Competitor Analysis")
company_input = st.text_input("Enter Company Name:")

if st.button("Find Competitors"):
    if company_input:
        result = get_competitor_analysis(company_input)
        result = result.replace("```", "")
        result = result.replace("json\n", "")
        result = json.loads(result)
        if "error" in result:
            st.error(result["error"])
        else:
            # Store the result in st.session_state
            st.session_state.competitor_data = result
            st.session_state.company_name = company_input # store company name for subsequent reruns.
            # Initialize competitor index
            st.session_state.competitor_index = 0
    else:
        st.warning("Please enter a valid company name.")

# Display Competitor Analysis (if data is available)
if "competitor_data" in st.session_state:
    format_competitor_analysis(st.session_state.competitor_data)

    # Export Data
    df = export_to_csv(st.session_state.competitor_data)
    csv = df.to_csv(index=False).encode('utf-8')

    # Download Button
    st.download_button(
        label="📥 Download Pros & Cons as CSV",
        data=csv,
        file_name="competitor_analysis.csv",
        mime="text/csv"
    )
