import streamlit as st
from g4f.client import Client
import re
from datetime import date, timedelta

# Streamlit Page Setup
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="centered"
)

# Custom Styling (Big Green Budget Card & Print Button)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Poppins:wght@400;600;700&display=swap');
    
    body {
        font-family: 'Noto Sans Gujarati', 'Noto Sans Devanagari', 'Poppins', sans-serif;
    }
    
    .main-title { text-align: center; color: #1E88E5; font-weight: bold; }
    .sub-title { text-align: center; color: #555555; }
    
    .budget-card {
        background-color: #E8F5E9;
        border: 2px solid #2E7D32;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }
    .budget-label {
        color: #1B5E20;
        font-size: 18px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .budget-amount {
        color: #2E7D32;
        font-size: 32px;
        font-weight: 800;
        margin-top: 5px;
    }
    
    /* Hide Streamlit UI elements when printing */
    @media print {
        header, footer, .stButton, .stSelectbox, .stRadio, .stTextInput, .stNumberInput, .stDateInput, .stMultiSelect, hr {
            display: none !important;
        }
        .printable-area {
            display: block !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("<h1 class='main-title' style='text-align:left;'>✈️ AI Travel Planner</h1>", unsafe_allow_html=True)
with col_head2:
    selected_language = st.selectbox("🌐 Language / ભાષા:", ["English", "ગુજરાતી (Gujarati)", "हिंदी (Hindi)"])

st.markdown("<p class='sub-title' style='text-align:left;'>Plan your perfect trip instantly with AI — Completely Free!</p>", unsafe_allow_html=True)
st.divider()

# Inputs Section
st.subheader("📍 1. Travel Route & Destination / રૂટ અને સ્થળ")

region = st.radio("Select Region:", ["All India", "Out of India"], horizontal=True)

india_destinations = [
    "Ahmedabad (Gujarat)", "Surat (Gujarat)", "Vadodara (Gujarat)", "Rajkot (Gujarat)", "Diut / Daman",
    "Goa", "Manali (Himachal Pradesh)", "Shimla (Himachal Pradesh)", "Leh Ladakh",
    "Jaipur (Rajasthan)", "Udaipur (Rajasthan)", "Jaisalmer (Rajasthan)",
    "Kerala (Munnar/Alleppey)", "Mumbai (Maharashtra)", "Mahabaleshwar (Maharashtra)",
    "Varanasi (Uttar Pradesh)", "Agra (Uttar Pradesh)", "Rishikesh / Haridwar (Uttarakhand)",
    "Darjeeling (West Bengal)", "Gangtok (Sikkim)", "Ooty (Tamil Nadu)", "Kodaikanal (Tamil Nadu)",
    "Amritsar (Punjab)", "Srinagar (Kashmir)", "Other (Type Manually)"
]

international_destinations = [
    "Dubai (UAE)", "Bangkok / Phuket (Thailand)", "Bali (Indonesia)", "Maldives", 
    "Singapore", "Kuala Lumpur (Malaysia)", "Paris (France)", "London (UK)", 
    "Tokyo (Japan)", "Rome (Italy)", "Switzerland", "New York (USA)", "Other (Type Manually)"
]

start_location = st.text_input("Departure City / ક્યાંથી નીકળવું છે:", value="Ahmedabad")

if region == "All India":
    selected_dest = st.selectbox("Select Destination:", india_destinations)
    if selected_dest == "Other (Type Manually)":
        destination = st.text_input("Enter Custom Destination:", placeholder="e.g. Somnath, Kutch, Saputara")
    else:
        destination = selected_dest
else:
    selected_dest = st.selectbox("Select Destination:", international_destinations)
    if selected_dest == "Other (Type Manually)":
        destination = st.text_input("Enter Custom Destination:", placeholder="e.g. Vietnam, Sydney, Istanbul")
    else:
        destination = selected_dest

st.divider()
st.subheader("👥 2. Travelers & Dates / મુસાફરો અને તારીખ")

col_p1, col_d1, col_d2 = st.columns([1, 1, 1])
with col_p1:
    travelers_count = st.number_input("Total Travelers", min_value=1, max_value=50, value=2, step=1)
with col_d1:
    start_date = st.date_input("Start Date", value=date.today() + timedelta(days=7))
with col_d2:
    end_date = st.date_input("End Date", value=date.today() + timedelta(days=10))

if end_date <= start_date:
    st.error("End Date must be after Start Date!")
    days = 1
else:
    days = (end_date - start_date).days
    st.info(f"🗓️ Duration: **{days} Days / {days-1} Nights**")

st.divider()
st.subheader("⚙️ 3. Preferences & Budget / પસંદગી અને બજેટ")

col_b1, col_b2 = st.columns(2)
with col_b1:
    budget = st.selectbox("Budget Category", ["Low Budget", "Moderate", "Luxury"])
with col_b2:
    group_type = st.selectbox("Group Type", ["Solo", "Friends", "Family", "Couple"])

interests = st.multiselect(
    "Preferences",
    ["Sightseeing", "Adventure & Sports", "Food & Dining", "Relaxation", "Culture & History", "Shopping"],
    default=["Sightseeing", "Food & Dining"]
)

st.divider()

if st.button("🚀 Generate Detailed Itinerary", type="primary", use_container_width=True):
    if not destination or not destination.strip():
        st.warning("Please select or enter a valid destination!")
    elif end_date <= start_date:
        st.error("Please select valid Start and End Dates!")
    else:
        with st.spinner("AI is crafting your complete travel route & budget... Please wait."):
            try:
                client = Client()
                currency_unit = "INR (₹)" if region == "All India" else "USD ($) / local currency"
                
                prompt = f"""
                You are a professional tour operator and travel planner.
                Create a highly detailed, beautifully spaced, and point-wise travel itinerary in {selected_language} language.

                TRIP DETAILS:
                - Route: From {start_location} to {destination} ({region})
                - Travel Dates: {start_date.strftime('%d %B %Y')} to {end_date.strftime('%d %B %Y')} ({days} Days)
                - Total Travelers: {travelers_count} Persons
                - Group Type: {group_type}
                - Budget Category: {budget}
                - Preferences: {', '.join(interests)}
                - Output Language: {selected_language}

                CRITICAL FORMATTING INSTRUCTIONS:
                1. Write the entire response strictly in {selected_language} with 100% perfect spelling, grammar, matra, raswai/dirghai, and jođakshar.
                2. On the FIRST LINE of your response, write the total budget estimate clearly as:
                   TOTAL BUDGET ESTIMATE: [Amount Range in {currency_unit}]
                3. Maintain proper spacing and clean headings.
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )

                output_text = response.choices[0].message.content

                if output_text:
                    st.session_state['itinerary'] = output_text
                    st.session_state['destination'] = destination
                    st.session_state['travelers'] = travelers_count
                    st.success("Your Complete Travel Plan is Ready!")

            except Exception as e:
                st.error(f"An error occurred while generating the plan: {str(e)}")

# Display Result Section
if 'itinerary' in st.session_state:
    itinerary_content = st.session_state['itinerary']
    travelers_num = st.session_state.get('travelers', travelers_count)
    
    # Extract Budget and Display in Big Green Box
    budget_match = re.search(r"TOTAL BUDGET ESTIMATE:\s*(.*)", itinerary_content, re.IGNORECASE)
    if budget_match:
        total_budget_str = budget_match.group(1).strip()
        st.markdown(
            f"""
            <div class="budget-card">
                <div class="budget-label">💰 TOTAL ESTIMATED BUDGET ({travelers_num} PERSONS)</div>
                <div class="budget-amount">{total_budget_str}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with st.container(border=True):
        st.markdown(itinerary_content)
    
    st.divider()
    
    # Direct Browser Print/Save as PDF Button (Guarantees 100% Perfect Matra & Fonts)
    st.components.v1.html(
        """
        <button onclick="window.parent.print()" style="
            background-color: #1E88E5;
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
        ">🖨️ Save as PDF / Print Itinerary</button>
        """,
        height=60
    )