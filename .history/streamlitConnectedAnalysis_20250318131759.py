import streamlit as st
import pandas as pd
import json
from google import genai
from dotenv import load_dotenv, set_key
import os

# Load DataFrame (Replace 'linkedin_info.csv' with actual file path)
linkedinInfo = pd.read_csv('B2B-business-dataset-samples-main/LinkedIn-company-info.csv')

# Load JSON file containing industry-wise grouped data
with open("grouped_companies.json", "r") as f:
    industry_data = json.load(f)

# Configure Gemini API (Replace 'YOUR_GEMINI_API_KEY' with your API key)
load_dotenv()
api_key = os.environ.get('geminiApi')
genai.configure(api_key=api_key)

def get_company_info(company_name):
    """Retrieve company row from DataFrame"""
    company_row = linkedinInfo[linkedinInfo['company_name'].str.lower() == company_name.lower()]
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
    prompt = f'''
    You are an AI assistant specializing in business analysis. Your task is to find the top 3 closest competitors to "{company_name}", 
    based on the following details:
    - Specialities: {company_info['specialties']}
    - Location: {company_info['formatted_locations']}
    - Description: {company_info['description']}
    
    The provided JSON contains a list of companies in the same industry. Compare their specialities, locations, and descriptions 
    to determine the 3 most similar competitors.
    
    Additionally, analyze customer reviews of the competitors' products (you may estimate based on the company descriptions). 
    Identify the advantages of "{company_name}" over competitors and the major cons of the competitors' offerings.
    
    Return a JSON response with the following structure:
    {
        "competitor_1": {"name": "", "pros": "", "cons": ""},
        "competitor_2": {"name": "", "pros": "", "cons": ""},
        "competitor_3": {"name": "", "pros": "", "cons": ""}
    }
    '''
    
    # Call Gemini API
    model = genai.GenerativeModel("gemini-2.0-flash")  # Adjust model if needed
    response = model.generate_content([{"role": "user", "content": prompt}, {"role": "system", "content": json.dumps(competitors_data)}])
    
    try:
        return json.loads(response.text)
    except:
        return {"error": "Failed to parse Gemini API response."}

# Streamlit UI
st.title("Company Competitor Analysis")
company_input = st.text_input("Enter Company Name:")

if st.button("Find Competitors"):
    if company_input:
        result = get_competitor_analysis(company_input)
        if "error" in result:
            st.error(result["error"])
        else:
            st.write("### Competitor Analysis Results")
            for key, data in result.items():
                st.subheader(data["name"])
                st.write(f"**Pros:** {data['pros']}")
                st.write(f"**Cons:** {data['cons']}")
    else:
        st.warning("Please enter a valid company name.")
