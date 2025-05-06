import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# 1. Fetch list of all programs (countries/regions)
@st.cache_data
def get_programs():
    url = "https://api.pota.app/programs"
    resp = requests.get(url)
    data = resp.json()
    return {entry["programName"]: entry["programPrefix"] for entry in data}

# 2. Get parks for a specific programPrefix
@st.cache_data
def get_parks(program_prefix):
    url = f"https://api.pota.app/program/parks/{program_prefix}"
    resp = requests.get(url)
    return resp.json()

st.set_page_config(layout='centered', page_title="UnPOTAd", page_icon=":fountain:")

# UI: Title
st.title("Unactivated POTA Sites by Country")

# Dropdown: Country/Region selection
programs = get_programs()
selected_country = st.selectbox("Select a Country/Region", list(programs.keys()), placeholder="Select or type a country/region", index=None)

if selected_country:
    prefix = programs[selected_country]
    parks = get_parks(prefix)

    # Filter parks with 0 activations
    unactivated = [
        park for park in parks if park.get("activations", 0) == 0
    ]

    st.markdown(f"### Found {len(unactivated)} unactivated parks in {selected_country}")

    # 3. Plot map with folium
    if unactivated:
        # Center the map on the first unactivated park
        first = unactivated[0]
        map_center = [first["latitude"], first["longitude"]]
        fmap = folium.Map(location=map_center, zoom_start=6)

        for park in unactivated:
            lat = park["latitude"]
            lon = park["longitude"]
            name = park["name"]
            ref = park["reference"]
            link = f"https://pota.app/#/park/{ref}"

            popup_html = f"""<b>{name}</b><br>
                             <a href="{link}" target="_blank">{ref}</a>"""

            folium.Marker(
                location=[lat, lon],
                tooltip=name,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(fmap)

        st_folium(fmap, width=700, height=700, returned_objects=[])
    else:
        st.info("No unactivated parks found for this country.")
