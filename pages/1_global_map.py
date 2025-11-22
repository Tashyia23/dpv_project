import streamlit as st
import plotly.express as px
from utils.loader import load_base_data
from utils.ui import header

# st.set_page_config(layout="wide")

# base_df = load_base_data()

# header(
#     "🗺 Global Air Pollution Map",
#     "Explore spatial patterns using choropleth mapping."
# )

# metric = st.selectbox(
#     "Choose pollutant",
#     ["aqi_value", "pm25_aqi_value", "no2_aqi_value", "co_aqi_value"],
# )

# # aggregate
# agg = base_df.groupby("country", as_index=False)[metric].mean()

# fig = px.choropleth(
#     agg,
#     locations="country",
#     locationmode="country names",
#     color=metric,
#     title="Global Pollution Levels",
#     color_continuous_scale="RdYlBu_r",
# )

# fig.update_geos(showframe=False, projection_type="natural earth")
# st.plotly_chart(fig, use_container_width=True)


   if page == "map":
        st.markdown(
            """
            <div class="page-header-card">
                <div class="page-header-title">🗺 Global Air Pollution Map (Interactive)</div>
                <div class="page-header-subtitle">
                    Use the controls on the left to adjust the metric, AQI categories, and minimum AQI threshold.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        default_metric_label = (
            "Overall AQI Value"
            if "Overall AQI Value" in metric_options
            else list(metric_options.keys())[0]
        )

        filters_col, map_col = st.columns([0.27, 0.73])

        # ---- Filters
        with filters_col:
            st.markdown(
                """
                <div class='filter-card'>
                    <div class='filter-title'>
                        <span class='icon'>⚙️</span><span>Settings</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )

            # Metric selector
            st.markdown("<div class='filter-label'>Pollution metric</div>", unsafe_allow_html=True)
            metric_label = st.selectbox(
                "",
                list(metric_options.keys()),
                index=list(metric_options.keys()).index(default_metric_label),
                key="map_metric",
            )
            metric_col = metric_options[metric_label]

            # AQI categories filter
            if "aqi_category" in base_df.columns:
                st.markdown("<div class='filter-label'>AQI category</div>", unsafe_allow_html=True)
                categories = sorted(base_df["aqi_category"].dropna().unique().tolist())
                selected_cats = st.multiselect(
                    "",
                    categories,
                    default=categories,
                    key="map_categories",
                )
            else:
                selected_cats = None

            # Minimum overall AQI
            if "aqi_value" in base_df.columns:
                st.markdown("<div class='filter-label'>Minimum overall AQI value</div>", unsafe_allow_html=True)
                min_val = float(base_df["aqi_value"].min())
                max_val = float(base_df["aqi_value"].max())
                min_threshold = st.slider(
                    "",
                    min_value=float(round(min_val, 1)),
                    max_value=float(round(max_val, 1)),
                    value=float(round(min_val, 1)),
                    step=1.0,
                    key="map_min_aqi",
                )
            else:
                min_threshold = None

            st.markdown("</div>", unsafe_allow_html=True)  # close filter-card

        # ---- Map
        with map_col:
            df_map = base_df.copy()

            if selected_cats:
                df_map = df_map[df_map["aqi_category"].isin(selected_cats)]
            if min_threshold is not None and "aqi_value" in df_map.columns:
                df_map = df_map[df_map["aqi_value"] >= min_threshold]

            if df_map.empty:
                st.warning("No data matches the current filters. Try relaxing them.")
            elif "country" not in df_map.columns:
                st.error("Column 'country' is missing in the dataset.")
            else:
                agg = df_map.groupby("country", as_index=False)[metric_col].mean().dropna()

                if agg.empty:
                    st.warning("No countries found after aggregation.")
                else:
                    # KPI cards
                    avg_val = agg[metric_col].mean()
                    worst_row = agg.loc[agg[metric_col].idxmax()]
                    best_row = agg.loc[agg[metric_col].idxmin()]

                    st.markdown("<div class='kpi-row'>", unsafe_allow_html=True)
                    k1, k2, k3 = st.columns(3)
                    with k1:
                        st.markdown(
                            f"""
                            <div class="kpi-card">
                                <div class="kpi-label">Global average</div>
                                <div class="kpi-value">{avg_val:.1f}</div>
                                <div class="kpi-sub">{metric_label}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with k2:
                        st.markdown(
                            f"""
                            <div class="kpi-card">
                                <div class="kpi-label">Most polluted</div>
                                <div class="kpi-value">{worst_row['country']}</div>
                                <div class="kpi-sub">{worst_row[metric_col]:.1f} {metric_label}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with k3:
                        st.markdown(
                            f"""
                            <div class="kpi-card">
                                <div class="kpi-label">Cleanest</div>
                                <div class="kpi-value">{best_row['country']}</div>
                                <div class="kpi-sub">{best_row[metric_col]:.1f} {metric_label}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                    n_countries = agg["country"].nunique()
                    summary_text = f"Showing {n_countries} countries · Metric: {metric_label}"
                    if min_threshold is not None:
                        summary_text += f" · Min overall AQI: {min_threshold:.0f}"
                    st.markdown(f"<div class='map-summary'>{summary_text}</div>", unsafe_allow_html=True)

                    vmin = float(agg[metric_col].min())
                    vmax = float(agg[metric_col].max())

                    st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                    fig = px.choropleth(
                        agg,
                        locations="country",
                        locationmode="country names",
                        color=metric_col,
                        color_continuous_scale="RdYlBu_r",
                        range_color=(vmin, vmax),
                        hover_name="country",
                        hover_data={metric_col: ":.1f"},
                    )
                    fig.update_geos(
                        showframe=False,
                        showcoastlines=True,
                        projection_type="natural earth",
                    )
                    fig.update_layout(
                        height=610,
                        margin=dict(l=0, r=0, t=10, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        coloraxis_colorbar=dict(
                            title=metric_label,
                            orientation="h",
                            y=-0.18,
                            x=0.5,
                            thickness=12,
                            len=0.80,
                        ),
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                    with st.expander("Show aggregated data table"):
                        st.dataframe(agg.rename(columns={metric_col: metric_label}))
