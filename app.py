import os
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

# App Header
st.title("🏫 Hong Kong Schools Directory")
st.markdown("Explore and filter top Hong Kong international and private schools.")

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# District Filter
all_districts = ["All"] + sorted([d for d in df["District"].unique() if d])
selected_district = st.sidebar.selectbox("Select District:", all_districts)

# Curriculum Filter
all_curriculums = ["All"] + sorted([c for c in df["Curriculum"].unique() if c])
selected_curriculum = st.sidebar.selectbox("Select Curriculum:", all_curriculums)

# Search Bar
search_query = st.sidebar.text_input("Search School Name:", "")

# Filter Data
filtered_df = df.copy()

if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]

if selected_curriculum != "All":
    filtered_df = filtered_df[filtered_df["Curriculum"] == selected_curriculum]

if search_query:
    filtered_df = filtered_df[filtered_df["Name of School"].str.contains(search_query, case=False, na=False)]

# Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Schools", len(df))
col2.metric("Matching Filters", len(filtered_df))
col3.metric("Districts Covered", len([d for d in df["District"].unique() if d]))

st.divider()

# Display School Cards
if filtered_df.empty:
    st.info("No schools match your search criteria. Try adjusting your filters.")
else:
    for _, row in filtered_df.iterrows():
        with st.container():
            st.subheader(row["Name of School"])
            
            c1, c2, c3 = st.columns(3)
            c1.write(f"📍 **District:** {row['District']}")
            c2.write(f"📚 **Curriculum:** {row['Curriculum']}")
            c3.write(f"🏫 **Type:** {row['Type']}")
            
            st.caption(f"🪜 Level: {row['🪜 Level']}")
            st.divider()
