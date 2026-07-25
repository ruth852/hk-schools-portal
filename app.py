import os
import urllib.parse
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hong Kong Schools Directory",
    page_icon="🏫",
    layout="wide"
)

@st.cache_data
def load_data():
    csv_file = "hongkong_schools.csv"
    if not os.path.exists(csv_file):
        st.error(f"❌ File `{csv_file}` not found.")
        st.stop()
        
    df = pd.read_csv(csv_file, engine="python", on_bad_lines="skip")
    df.columns = df.columns.astype(str).str.strip()
    
    # Ensure optional columns exist safely
    for col in ["Photo URL", "Annual Fees", "Description"]:
        if col not in df.columns:
            df[col] = ""
            
    return df.fillna("")

df = load_data()

# Header
st.title("🏫 Hong Kong Schools Directory")
st.markdown("Explore verified school profiles, curriculum streams, and fee structures.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

all_districts = ["All"] + sorted([d for d in df["District"].unique() if d])
selected_district = st.sidebar.selectbox("Select District:", all_districts)

all_curriculums = ["All"] + sorted([c for c in df["Curriculum"].unique() if c])
selected_curriculum = st.sidebar.selectbox("Select Curriculum:", all_curriculums)

search_query = st.sidebar.text_input("Search School Name:", "")

# Filter Logic
filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_curriculum != "All":
    filtered_df = filtered_df[filtered_df["Curriculum"] == selected_curriculum]

if search_query:
    filtered_df = filtered_df[filtered_df["Name of School"].str.contains(search_query, case=False, na=False)]

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Schools", len(df))
col2.metric("Matching Search", len(filtered_df))
col3.metric("Districts", len([d for d in df["District"].unique() if d]))

st.divider()

# Clickable School Cards
if filtered_df.empty:
    st.info("No schools match your search criteria. Try adjusting your filters.")
else:
    for _, row in filtered_df.iterrows():
        school_name = row["Name of School"]
        district = row["District"]
        curriculum = row["Curriculum"]
        school_type = row["Type"]
        level = row["🪜 Level"]
        annual_fees = str(row.get("Annual Fees", "")).strip()
        description = str(row.get("Description", "")).strip()
        photo_url = str(row.get("Photo URL", "")).strip()

        # Accordion Profile Card
        with st.expander(f"🏫 **{school_name}**  —  *{district} | {curriculum}*", expanded=False):
            col_img, col_info = st.columns([1, 2])
            
            # Photo Display
            with col_img:
                if photo_url and photo_url.startswith("http"):
                    st.image(photo_url, use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div style="background-color: #f0f2f6; padding: 45px; text-align: center; border-radius: 8px;">
                            <span style="font-size: 50px;">🏫</span>
                            <p style="color: #666; margin-top: 5px; font-size: 13px;">Campus View</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            # Facts & Description
            with col_info:
                st.subheader(school_name)
                
                # Neutral Description
                if description:
                    st.markdown(f"*{description}*")
                    st.write("")
                
                d1, d2 = st.columns(2)
                with d1:
                    st.write(f"📍 **District:** {district}")
                    st.write(f"📚 **Curriculum:** {curriculum}")
                with d2:
                    st.write(f"🏛️ **School Type:** {school_type}")
                    st.write(f"🪜 **Grade Level:** {level}")
                
                # Fees
                if annual_fees:
                    st.success(f"💰 **Annual Tuition Fees:** {annual_fees}")
                else:
                    st.info("💰 **Annual Tuition Fees:** Contact school for current structure")
                
                st.divider()
                
                # Links & Direct WhatsApp Button
                query_str = urllib.parse.quote(f"{school_name} Hong Kong")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
                
                msg = urllib.parse.quote(f"Hi! I would like to enquire about {school_name}.")
                whatsapp_url = f"https://wa.me/85296601584?text={msg}"
                
                b1, b2 = st.columns(2)
                with b1:
                    st.link_button("💬 Enquire via WhatsApp", whatsapp_url, use_container_width=True)
                with b2:
                    st.link_button("📍 View Location on Google Maps", maps_url, use_container_width=True)
