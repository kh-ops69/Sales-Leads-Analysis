# Sales-Lead-Analysis (Proof-of-Concept)

## Overview
This project is a proof-of-concept (PoC) for analyzing competitors and identifying business strengths/weaknesses using a LinkedIn dataset and Gemini AI. The application is built with Streamlit for UI interaction.

## Installation
To set up and run this project, follow these steps:

### 1. Clone the Repository
```sh
git clone <repository_url>
cd <repository_name>
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment:
```sh
python -m venv leadenv  # Create virtual environment
source leadenv/bin/activate  # macOS/Linux
leadenv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Gemini API Key
- Create a `.env` file in the root directory of your project.
- Add your Gemini API key to the `.env` file as follows:
```
geminiApi=YOUR_GEMINI_API_KEY
```
- Ensure you have the `python-dotenv` package installed (it should be in `requirements.txt`). This allows your application to read the API key from the `.env` file.

### 5. Run the Application
```sh
streamlit run app.py
```

## Project Structure
```
├── streamlitConnectedAnalysis.py          # Main Streamlit application
├── datasetAnalysis.ipynb         # Basic Preliminary Dataset Analysis
├── B2B-business-dataset-samples-main/linkedin_data.csv  # Dataset Used
├── requirements.txt    # Dependencies
├── .gitignore        # Ignore unnecessary files (including virtual environment and .env)
├── README.md         # Project documentation
├── leadenv/          # Virtual environment (excluded from Git)
└── .env              # Environment variables (excluded from Git)
```

## Usage
- Enter a company name in the Streamlit UI.
- The app retrieves details from the dataset.
- Competitors are identified based on industry, location, and specialities.
- Gemini AI processes the data to provide insights on competitors.
- The output displays business strengths and weaknesses.

## Contributing
Feel free to contribute by opening an issue or submitting a pull request.
