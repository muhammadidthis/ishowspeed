import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Content Creator Comparison")
st.markdown("<h1 style='text-align: center;'>📈 Comparison with Other Content Creators</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- PROFILE CARDS ---
st.markdown("### 🧑‍🎤 Creator Profiles")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("ishowspeed.jpeg", caption="IShowSpeed", use_column_width=True)
    st.markdown("""
    - **Real Name**: Darren Watkins Jr.  
    - **Platform**: YouTube, Kick, TikTok  
    - **Known For**: Chaotic energy, football fandom, meme moments  
    - **Target Audience**: Gen Z, teens  
    """)

with col2:
    st.image("mrbeast.png", caption="MrBeast", use_column_width=True)
    st.markdown("""
    - **Real Name**: Jimmy Donaldson  
    - **Platform**: YouTube  
    - **Known For**: High-budget challenges, philanthropy  
    - **Target Audience**: Family-friendly, wide age range  
    """)

with col3:
    st.image("pewdiepie.jpg", caption="PewDiePie", use_column_width=True)
    st.markdown("""
    - **Real Name**: Felix Kjellberg  
    - **Platform**: YouTube  
    - **Known For**: Gaming, commentary, memes  
    - **Target Audience**: Millennials, older Gen Z  
    """)

st.markdown("---")

# --- COMPARISON TABLE ---
st.markdown("### 📊 Key Comparison Table")

comparison_data = {
    "Feature": [
        "Platform Focus", "Content Style", "Virality Strategy", "Audience",
        "Monetization", "Peak Period"
    ],
    "IShowSpeed": [
        "YouTube, TikTok, Kick", "Chaotic, reactive", "Shorts, meme clips", "Gen Z, Teens",
        "Donations, sponsors, viral traffic", "2022–Present"
    ],
    "MrBeast": [
        "YouTube", "High-effort challenges", "Giveaways, big stunts", "Family, broad",
        "Sponsors, merch, ad revenue", "2020–Present"
    ],
    "PewDiePie": [
        "YouTube", "Gaming, comedy", "Mass following over time", "Millennials, gamers",
        "Ad revenue, brand deals", "2013–2020"
    ]
}

df_compare = st.data_editor(
    comparison_data,
    column_config={
        "Feature": st.column_config.TextColumn(width="small")
    },
    use_container_width=True,
    disabled=True,
    hide_index=True
)

st.markdown("---")

# --- WHAT SETS SPEED APART ---
st.markdown("### 🔥 What Sets IShowSpeed Apart?")
st.markdown("""
- **Emotional chaos**: Speed’s high-energy, unpredictable streams make him endlessly watchable.  
- **Meme magnet**: His moments (like barking or football meltdowns) are made for virality.  
- **Multi-platform exposure**: Simultaneously trending on TikTok, YouTube, and Kick.  
- **Unfiltered personality**: Relatable to teens who see him as “one of them.”  
""")

# --- LESSONS FROM HIS RISE ---
st.markdown("### 🧠 Lessons from IShowSpeed’s Success")
st.markdown("""
1. **Authenticity wins** – Be bold, emotional, and real.  
2. **Short-form rules** – Meme-worthy content spreads like wildfire on TikTok & Shorts.  
3. **Build across platforms** – Don’t rely on just one audience base.  
""")
