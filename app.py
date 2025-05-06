import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

@st.cache_data
def get_programs():
    url = "https://api.pota.app/programs"
    resp = requests.get(url)
    data = resp.json()
    return {entry["programName"]: entry["programPrefix"] for entry in data}


def get_parks(program_prefix):
    url = f"https://api.pota.app/program/parks/{program_prefix}"
    resp = requests.get(url)
    return resp.json()

st.set_page_config(layout='centered', page_title="UnPOTAd", page_icon=":fountain:")


st.title("Unactivated POTA Sites by Country")


programs = get_programs()
selected_country = st.selectbox("Select a Country/Region", list(programs.keys()), placeholder="Select or type a country/region", index=None)

if selected_country:
    prefix = programs[selected_country]
    parks = get_parks(prefix)


    unactivated = [
        park for park in parks if park.get("activations", 0) == 0
    ]

    st.markdown(f"### Found {len(unactivated)} unactivated parks in {selected_country}")


    if unactivated:

        first = unactivated[0]
        map_center = [first["latitude"], first["longitude"]]
        fmap = folium.Map(location=map_center, zoom_start=6)

        marker_cluster = MarkerCluster().add_to(fmap)

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
            ).add_to(marker_cluster)

        st_folium(fmap, width=700, height=700, returned_objects=[])
    else:
        st.info("No unactivated parks found for this country.")

with st.expander("What is UnPOTAd?", icon="❓"):
    st.markdown('''
        A tool that helps you find unactivated POTA sites in your country. It retrieves all the parks and checks the number of activations. Designed by [GM5ALX](https://gm5alx.uk), see the [source code](https://github.com/alexjj/unpotad). Your responsibility to check the validity of the data and the parks. The data is provided by [POTA](https://pota.app) and is not guaranteed to be accurate or up-to-date. Use at your own risk.
    ''')
