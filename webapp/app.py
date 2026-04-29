import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np

DATA_PATH = "../data/processed/merged_crash_vehicle_data_with_highways.csv"

st.set_page_config(page_title="Crash Map", layout="wide")
st.title("San Jose Crash Map")

SOUTH_BAY = {"lat_min": 36.9, "lat_max": 37.5, "lon_min": -122.2, "lon_max": -121.6}

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df.dropna(subset=["Latitude", "Longitude"])
    df = df[
        df["Latitude"].between(SOUTH_BAY["lat_min"], SOUTH_BAY["lat_max"]) &
        df["Longitude"].between(SOUTH_BAY["lon_min"], SOUTH_BAY["lon_max"])
    ]
    # Deduplicate to one row per crash event (multiple vehicle rows per crash)
    crash_dedup = [c for c in ["Latitude", "Longitude", "CrashDateTime"] if c in df.columns]
    if crash_dedup:
        df = df.drop_duplicates(subset=crash_dedup, keep="first")
    return df

DETAIL_COLS = [
    "Latitude", "Longitude",
    # identity
    "TcrNumber", "CrashDateTime", "crash_date", "crash_hour", "crash_dayofweek", "data_source",
    # location
    "AStreetName", "BStreetName", "ProximityToIntersection", "DirectionFromIntersection",
    # injuries
    "injury_severity", "FatalInjuries_crash", "SevereInjuries_crash",
    "ModerateInjuries_crash", "MinorInjuries_crash",
    # crash characteristics
    "CollisionType", "PrimaryCollisionFactor", "VehicleInvolvedWith",
    "VehicleCount", "SpeedingFlag", "HitAndRunFlag", "PedestrianAction",
    # road & environment
    "RoadwaySurface", "RoadwayCondition", "TrafficControl", "Weather", "Lighting",
]

SEVERITY_LABELS = {0: "No Injury / Property Damage", 1: "Minor Injury", 2: "Severe Injury", 3: "Fatal"}
DAY_LABELS = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

df = load_data(DATA_PATH)

st.sidebar.header("Filters")
if "injury_severity" in df.columns:
    severities = sorted([x for x in df["injury_severity"].dropna().unique()])
    selected = st.sidebar.multiselect("Injury severity", severities, default=severities)
    df = df[df["injury_severity"].isin(selected)]

view = pdk.ViewState(
    latitude=37.3382,
    longitude=-121.8863,
    zoom=11,
    pitch=0,
)

mode = st.sidebar.radio("Map mode", ["Points", "Heatmap"], index=1)

detail_cols_present = [c for c in DETAIL_COLS if c in df.columns]

# One dot per unique location for the Points layer; full df used for heatmap density
location_deduped = df.drop_duplicates(subset=["Latitude", "Longitude"], keep="first")

if mode == "Points":
    tooltip = {
        "html": (
            "<b>{AStreetName} & {BStreetName}</b><br/>"
            "📅 {CrashDateTime}<br/>"
            "💥 {CollisionType}<br/>"
            "🌤️ {Weather} &nbsp;|&nbsp; {Lighting}<br/>"
            "⚠️ Severity: {injury_severity}"
        ),
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "white",
            "fontSize": "13px",
            "padding": "10px",
            "borderRadius": "6px",
            "maxWidth": "280px",
        },
    }
    layer = pdk.Layer(
        "ScatterplotLayer",
        id="crashes",
        data=location_deduped[detail_cols_present],
        get_position="[Longitude, Latitude]",
        get_radius=5,
        radius_units="meters",
        get_fill_color=[255, 0, 0, 150],
        pickable=True,
    )
else:
    tooltip = None
    layer = pdk.Layer(
        "HeatmapLayer",
        data=df[["Latitude", "Longitude"]],
        get_position="[Longitude, Latitude]",
        aggregation="MEAN",
        color_range=[
            [0, 0, 0, 0],
            [255, 255, 0, 200],
            [255, 165, 0, 200],
            [255, 0, 0, 255],
        ],
        threshold=0.05,
        radius_pixels=30,
        pickable=False,
    )

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip=tooltip,
)

if "clicked_lat" not in st.session_state:
    st.session_state["clicked_lat"] = None
    st.session_state["clicked_lon"] = None

if mode == "Points":
    event = st.pydeck_chart(deck, selection_mode="single-object", on_select="rerun", width="stretch")
    st.caption(f"Showing {len(location_deduped):,} unique locations ({len(df):,} total crashes) — hover to preview, click to pin details below")

    # Update session state when a new point is clicked
    try:
        objects = event.selection.objects
        for layer_hits in objects.values():
            if layer_hits:
                st.session_state["clicked_lat"] = layer_hits[0].get("Latitude")
                st.session_state["clicked_lon"] = layer_hits[0].get("Longitude")
                break
    except Exception:
        pass

    clicked_lat = st.session_state["clicked_lat"]
    clicked_lon = st.session_state["clicked_lon"]

    if clicked_lat is not None and clicked_lon is not None:
        crashes_here = df[
            (df["Latitude"] == clicked_lat) & (df["Longitude"] == clicked_lon)
        ][detail_cols_present].copy()

        if crashes_here.empty:
            st.info("Hover over a point to see crash info. Click a point to pin details here.")
        else:
            a = str(crashes_here.iloc[0].get("AStreetName") or "")
            b = str(crashes_here.iloc[0].get("BStreetName") or "")
            location_title = f"{a} & {b}" if (a and b) else (a or b or "Selected Location")

            st.subheader(f"📍 {location_title}")

            if len(crashes_here) > 1:
                date_options = crashes_here["CrashDateTime"].fillna("Unknown").tolist()
                chosen_date = st.selectbox(
                    f"{len(crashes_here)} crashes at this location — select one:",
                    date_options,
                )
                row = crashes_here[crashes_here["CrashDateTime"] == chosen_date].iloc[0].to_dict()
            else:
                row = crashes_here.iloc[0].to_dict()

            def val(key):
                v = row.get(key)
                return str(v) if v not in (None, "", float("nan")) else "—"

            sev_raw = row.get("injury_severity")
            sev_label = SEVERITY_LABELS.get(int(sev_raw), str(sev_raw)) if sev_raw is not None else "—"
            proximity = val("ProximityToIntersection")
            direction = val("DirectionFromIntersection")
            loc_detail = f"{direction} of intersection" if direction != "—" and proximity == "Related" else proximity
            hour = row.get("crash_hour")
            hour_str = f"{int(hour):02d}:00" if hour is not None else "—"
            dow = row.get("crash_dayofweek")
            dow_str = DAY_LABELS.get(int(dow), "—") if dow is not None else "—"

            st.caption(f"Report #{val('TcrNumber')} · {val('data_source')}")
            st.divider()

            st.markdown("**📋 Overview**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Date", val("crash_date"))
            c2.metric("Time", hour_str)
            c3.metric("Day", dow_str)
            c4.metric("Severity", sev_label)

            st.markdown("**📍 Location**")
            c1, c2 = st.columns(2)
            c1.metric("Intersection", location_title)
            c2.metric("Proximity", loc_detail)

            st.markdown("**🚗 Crash Characteristics**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Collision Type", val("CollisionType"))
            c2.metric("Primary Factor", val("PrimaryCollisionFactor"))
            c3.metric("Involved With", val("VehicleInvolvedWith"))
            c4.metric("Vehicles", val("VehicleCount"))

            c1, c2, c3 = st.columns(3)
            c1.metric("Speeding", val("SpeedingFlag"))
            c2.metric("Hit & Run", val("HitAndRunFlag"))
            c3.metric("Pedestrian Action", val("PedestrianAction"))

            st.markdown("**🤕 Injuries**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Fatal", val("FatalInjuries_crash"))
            c2.metric("Severe", val("SevereInjuries_crash"))
            c3.metric("Moderate", val("ModerateInjuries_crash"))
            c4.metric("Minor", val("MinorInjuries_crash"))

            st.markdown("**🌤️ Road & Environment**")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Weather", val("Weather"))
            c2.metric("Lighting", val("Lighting"))
            c3.metric("Road Surface", val("RoadwaySurface"))
            c4.metric("Traffic Control", val("TrafficControl"))
    else:
        st.info("Hover over a point to see crash info. Click a point to pin details here.")
else:
    st.pydeck_chart(deck, width="stretch")
    st.caption(f"Showing {len(df):,} crashes")