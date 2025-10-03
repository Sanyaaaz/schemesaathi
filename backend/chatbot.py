import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK data (only first time)
nltk.download("punkt")
nltk.download("stopwords")

# Load dataset
df = pd.read_excel("IBM Dataset Q-A.xlsx")
df.columns = df.columns.str.strip()  
df.columns = df.columns.str.replace("\n", "") 
df.columns = df.columns.str.replace("/", "_") 

# Fill missing values safely
df["Income"] = df["Income"].fillna("No specific requirement")
df["sex"] = df["sex"].fillna("Any")
df["State"] = df["State"].fillna("All States")

# -------------------- Utility Functions --------------------

def check_age(age, age_group):
    if pd.isna(age_group):
        return True
    age_group_str = str(age_group).lower()

    if "-" in age_group_str:
        try:
            low, high = map(int, age_group_str.split("-"))
            return low <= age <= high
        except ValueError:
            pass
    elif "below" in age_group_str:
        try:
            return age < int(age_group_str.split()[-1])
        except ValueError:
            pass
    elif "above" in age_group_str:
        try:
            return age > int(age_group_str.split()[-1])
        except ValueError:
            pass
    return True

def get_schemes(age=None, sex=None, state=None, category=None, keywords=None):
    result = df.copy()

    # Filters (state, sex, age, category)
    if state:
        result = result[(result["State"].str.lower() == state.lower()) | 
                        (result["State"].str.lower() == "All States".lower())]
    if sex:
        result = result[(result["sex"].str.lower() == sex.lower()) | (result["sex"].str.lower() == "Any".lower())]
    if age:
        result = result[result["Age group"].apply(lambda grp: check_age(age, grp))]
    if category:
        result = result[result["Category"].str.lower() == category.lower()]

    # Keyword filter
    if keywords:
        keywords = [k.lower() for k in keywords if k not in stopwords.words("english")]
        mask = result.apply(lambda row: any(
            k in str(row.get("Scheme name", "")).lower() or 
            k in str(row.get("Benefits of scheme_Details", "")).lower()
            for k in keywords
        ), axis=1)
        result = result[mask]

    # Select only existing columns
    columns_to_return = []
    for col in ["Scheme name", "Benefits of scheme_Details", "Eligibility", "Output", "Link"]:
        if col in result.columns:
            columns_to_return.append(col)

    return result[columns_to_return]


# -------------------- Conversation Logic --------------------

user_sessions = {}

# Dropdown options
AGE_OPTIONS = ["18-30", "31-50", "51-70", "Above 70"]
SEX_OPTIONS = ["Male", "Female", "Other"]
STATE_OPTIONS = list(df["State"].dropna().unique())
CATEGORY_OPTIONS = list(df["Category"].dropna().unique())

QUESTIONS = [
    ("age", "Select your age group:", AGE_OPTIONS),
    ("sex", "Select your gender:", SEX_OPTIONS),
    ("state", "Select your state:", STATE_OPTIONS),
    ("category", "Select scheme category:", CATEGORY_OPTIONS)
]

def extract_keywords(message):
    tokens = word_tokenize(message.lower())
    tokens = [t for t in tokens if t.isalpha() and t not in stopwords.words("english")]
    return tokens

def chatbot_conversation(user_id, message=None):
    # If user not in session, create
    if user_id not in user_sessions:
        user_sessions[user_id] = {"step": 0, "data": {}}
        return {"text": "Welcome to SchemeSathi! Click below to start.", 
                "type": "start", 
                "options": ["Start"]}

    session = user_sessions[user_id]

    # If user clicks Start
    if message and message.lower() == "start":
        session["step"] = 0
        session["data"] = {}
        key, text, options = QUESTIONS[0]
        return {"text": text, "type": "dropdown", "options": options}

    # If step < len(QUESTIONS), save dropdown answer
    if session["step"] < len(QUESTIONS):
        key, _, _ = QUESTIONS[session["step"]]
        session["data"][key] = message
        session["step"] += 1

        if session["step"] < len(QUESTIONS):
            next_key, next_text, next_options = QUESTIONS[session["step"]]
            return {"text": next_text, "type": "dropdown", "options": next_options}

    # If all questions answered OR user typed free text
    data = session["data"].copy()
    keywords = extract_keywords(message) if message else []

    # Parse age from selected group if available
    age = None
    if "age" in data and data["age"]:
        age_str = data["age"]
        if "-" in age_str:
            age = int(age_str.split("-")[0])
        elif "Above" in age_str:
            age = 71

    # Get schemes
    result = get_schemes(
        age=age,
        sex=data.get("sex"),
        state=data.get("state"),
        category=data.get("category"),
        keywords=keywords
    )

    # Format reply
    if result.empty:
        reply = "⚠️ Sorry, no schemes found for your criteria."
    else:
        reply = "✅ Here are the schemes you can apply for:\n"
        for i, (_, row) in enumerate(result.iterrows(), 1):
            reply += f"\n{i}. {row['Scheme name']}"
            if 'Eligibility' in row:
                reply += f"\n   Eligibility: {row['Eligibility']}"
            reply += f"\n   Details: {row['Benefits of scheme_Details']}"

            if 'Output' in row:
                reply += f"\n   Apply link: {row['Output']}\n"

    # Reset session
    user_sessions[user_id] = {"step": 0, "data": {}}
    return {"text": reply, "type": "text"}
