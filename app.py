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
    return df.fillna("")

df = load_data()

# Header
st.title("🏫 Hong Kong Schools Directory")
st.markdown("Click on any school row below to expand and view full details, location, and search links.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

all_districts = ["All"] + sorted([d for d in df["District"].unique() if d])
selected_district = st.sidebar.selectbox("Select District:", all_districts)

all_curriculums = ["All"] + sorted([c for c in df["Curriculum"].unique() if c])
selected_curriculum = st.sidebar.selectbox("Select Curriculum:", all_curriculums)

search_query = st.sidebar.text_input("Search School Name:", "")

# Filter Data Logic
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

# Interactive Clickable List
if filtered_df.empty:
    st.info("No schools match your search criteria. Try adjusting your filters.")
else:
    for _, row in filtered_df.iterrows():
        school_name = row["Name of School"]
        district = row["District"]
        curriculum = row["Curriculum"]
        school_type = row["Type"]
        level = row["🪜 Level"]
        photo_url = str(row.get("Photo URL", "")).strip()

        # Each school is a clickable drawer
        with st.expander(f"🏫 **{school_name}**  —  *{district} | {curriculum}*", expanded=False):
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                if photo_url and photo_url.startswith("http"):
                    st.image(photo_url, use_container_width=True)
                else:
                    st.markdown(
                        """
                        <div style="background-color: #f0f2f6; padding: 35px; text-align: center; border-radius: 8px;">
                            <span style="font-size: 50px;">🏫</span>
                            <p style="color: #666; margin-top: 5px; font-size: 13px;">Campus View</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )

            with col_info:
                st.subheader(school_name)
                
                d1, d2 = st.columns(2)
                with d1:
                    st.write(f"📍 **District:** {district}")
                    st.write(f"📚 **Curriculum:** {curriculum}")
                with d2:
                    st.write(f"🏛️ **School Type:** {school_type}")
                    st.write(f"🪜 **Grade Level:** {level}")
                
                st.divider()
                
                # Dynamic Links for Maps & Search
                query_str = urllib.parse.quote(f"{school_name} Hong Kong")
                maps_url = f"https://www.google.com/maps/search/?api=1&query={query_str}"
                search_url = f"https://www.google.com/search?q={query_str}+admissions+fees"
                
                b1, b2 = st.columns(2)
                b1.markdown(f"👉 [📍 **View on Google Maps**]({maps_url})")
                b2.markdown(f"👉 [🔍 **Search Admissions & Fees**]({search_url})")
