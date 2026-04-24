import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json

# Set page config
st.set_page_config(
    page_title="DCF Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header"> DCF Data Visualization Dashboard</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Dataset", [
    "Lawrence 2026 Q1 Dashboard",
    "Race by Town Demographics",
    "Student Discipline Data",
   # "Data Overview"
])

# Load data functions
@st.cache_data
def load_lawrence_data():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "lawrence_2026_q1_cleaned.json"), 'r') as f:
            data = json.load(f)

        # Convert the nested dictionary structure to a flat DataFrame
        all_records = []

        # Map section names to section numbers (based on the dashboard logic)
        section_mapping = {
            'placement_type': 21,
            'race_in_placement': 22,
            'age_group_in_placement': 23,
            'primary_language_in_placement': 24,
            'permanency_plan': 25,
            'time_in_placement': 26,
            'gender_identity': 27,
            'sexual_orientation_section_26': 28,
            'intake_type': 29
        }

        for section_name, records in data.items():
            if section_name != 'anomalies' and isinstance(records, list):
                section_num = section_mapping.get(section_name, 0)
                for record in records:
                    record_copy = record.copy()
                    record_copy['section'] = section_num
                    all_records.append(record_copy)

        df = pd.DataFrame(all_records)
        return df
    except Exception as e:
        st.error(f"Lawrence data not found. Please run the Lawrence dashboard script first. Error: {e}")
        return None

@st.cache_data
def load_race_data():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_excel(os.path.join(script_dir, "data_inputs", "Race by Town.xlsx"))

        # Clean column names (same as in race_by_town_viz.py)
        df.columns = ['Demographic', 'North Andover', 'Methuen', 'Lawrence', 'Andover CDP', 'United States']

        # Filter out population estimates (keep percentages)
        df_pct = df[df['Demographic'].str.contains('percent')].copy()

        # Clean demographic labels
        df_pct['Demographic'] = df_pct['Demographic'].str.replace(', percent', '').str.replace(' alone', '')

        # Convert to numeric
        for col in df_pct.columns[1:]:
            df_pct[col] = pd.to_numeric(df_pct[col], errors='coerce')

        return df_pct
    except Exception as e:
        st.error(f"Race by town data not found. Error: {e}")
        return None

@st.cache_data
def load_discipline_data():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_json(os.path.join(script_dir, "student_discipline_cleaned.json"))
        return df
    except Exception as e:
        st.error(f"Student discipline data not found. Please run the discipline visualization script first. Error: {e}")
        return None

SECTION_DISPLAY = {
    'placement_type': 'Placement Type',
    'race_in_placement': 'Race',
    'age_group_in_placement': 'Age Group',
    'primary_language_in_placement': 'Primary Language',
    'permanency_plan': 'Permanency Plan',
    'time_in_placement': 'Continuous Time in Placement',
    'gender_identity': 'Gender Identity',
    'sexual_orientation_section_26': 'Sexual Orientation',
    'intake_type': 'Intake Type'
}

LAWRENCE_SHEETS = ['2025 q3', '2025 q4', '2026 q1']
LAWRENCE_SHEET_LABELS = {
    '2025 q3': '2025 Q3',
    '2025 q4': '2025 Q4',
    '2026 q1': '2026 Q1'
}

LAWRENCE_SECTION_CONFIG = {
    '2026 q1': {
        'placement_type': {'slice': slice(39, 51), 'cols': [0, 1, 2], 'exclude': ['21.', 'Total In-Placement']},
        'race_in_placement': {'slice': slice(53, 60), 'cols': [0, 1, 2], 'exclude': ['22.', 'Total In-Placement']},
        'age_group_in_placement': {'slice': slice(55, 61), 'cols': [6, 7], 'exclude': ['23.', 'Total In-Placement']},
        'primary_language_in_placement': {'slice': slice(42, 51), 'cols': [6, 7, 8], 'exclude': ['19.', 'Total Consumers']},
        'permanency_plan': {'slice': slice(63, 70), 'cols': [0, 1, 2], 'exclude': ['28.', 'Total In-Placement']},
        'time_in_placement': {'slice': slice(92, 97), 'cols': [6, 9, 10], 'exclude': ['27.', 'Total In-Placement']},
        'gender_identity': {'slice': slice(68, 76), 'cols': [6, 9, 10], 'exclude': ['25.', 'Total In-Placement']},
        'sexual_orientation_section_26': {'slice': slice(80, 90), 'cols': [6, 9, 10], 'exclude': ['26.', 'Total In-Placement']},
        'intake_type': {'slice': slice(32, 36), 'cols': [0, 1, 2], 'exclude': ['20.', 'Total In-Placement']},
    },
    '2025 q3': {
        'placement_type': {'slice': slice(40, 51), 'cols': [0, 1, 2], 'exclude': ['21.', 'Total In-Placement']},
        'race_in_placement': {'slice': slice(54, 61), 'cols': [0, 1, 2], 'exclude': ['22.', 'Total In-Placement']},
        'age_group_in_placement': {'slice': slice(54, 59), 'cols': [6, 7], 'exclude': ['23.', 'Total In-Placement']},
        'primary_language_in_placement': {'slice': slice(42, 51), 'cols': [6, 7, 8], 'exclude': ['19.', 'Total Consumers']},
        'permanency_plan': {'slice': slice(64, 71), 'cols': [0, 1, 2], 'exclude': ['28.', 'Total In-Placement']},
        'time_in_placement': {'slice': slice(89, 95), 'cols': [6, 9, 10], 'exclude': ['27.', 'Total In-Placement']},
        'gender_identity': {'slice': slice(67, 76), 'cols': [6, 9, 10], 'exclude': ['25.', 'Total In-Placement']},
        'sexual_orientation_section_26': {'slice': slice(78, 87), 'cols': [6, 9, 10], 'exclude': ['26.', 'Total In-Placement']},
        'intake_type': {'slice': slice(34, 37), 'cols': [0, 1, 2], 'exclude': ['20.', 'Total In-Placement']},
    },
    '2025 q4': {
        'placement_type': {'slice': slice(40, 51), 'cols': [0, 1, 2], 'exclude': ['21.', 'Total In-Placement']},
        'race_in_placement': {'slice': slice(54, 61), 'cols': [0, 1, 2], 'exclude': ['22.', 'Total In-Placement']},
        'age_group_in_placement': {'slice': slice(54, 59), 'cols': [6, 7], 'exclude': ['23.', 'Total In-Placement']},
        'primary_language_in_placement': {'slice': slice(42, 51), 'cols': [6, 7, 8], 'exclude': ['19.', 'Total Consumers']},
        'permanency_plan': {'slice': slice(64, 71), 'cols': [0, 1, 2], 'exclude': ['28.', 'Total In-Placement']},
        'time_in_placement': {'slice': slice(90, 96), 'cols': [6, 9, 10], 'exclude': ['27.', 'Total In-Placement']},
        'gender_identity': {'slice': slice(67, 76), 'cols': [6, 9, 10], 'exclude': ['25.', 'Total In-Placement']},
        'sexual_orientation_section_26': {'slice': slice(78, 88), 'cols': [6, 9, 10], 'exclude': ['26.', 'Total In-Placement']},
        'intake_type': {'slice': slice(34, 37), 'cols': [0, 1, 2], 'exclude': ['20.', 'Total In-Placement']},
    },
}


def parse_numeric(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and np.isnan(value):
            return None
        return float(value)
    text = str(value).strip()
    if text in ['', '*', 'nan', 'None', 'NA', 'N/A']:
        return None
    text = text.replace('%', '')
    text = text.replace(',', '')
    text = text.replace('\n', ' ')
    for token in text.split():
        try:
            return float(token)
        except Exception:
            continue
    return None


def parse_count(value):
    numeric = parse_numeric(value)
    if numeric is None:
        return None
    return int(numeric)


def clean_label(value):
    if isinstance(value, str):
        return value.strip()
    return value


def parse_lawrence_section(df, section_config):
    rows = df.iloc[section_config['slice'], section_config['cols']].copy()
    rows = rows.dropna(how='all', subset=[section_config['cols'][0]])
    parsed = []
    for _, row in rows.iterrows():
        label = clean_label(row.iloc[0])
        if not label:
            continue
        if any(str(label).startswith(ex) for ex in section_config['exclude']):
            continue
        count = parse_count(row.iloc[1])
        if count is None:
            continue
        parsed.append({'label': label, 'count': count})
    return pd.DataFrame(parsed)


def load_lawrence_quarters():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workbook_path = os.path.join(script_dir, "data_inputs", "Updated_Lawrence Quarters.xlsx")
    if not os.path.exists(workbook_path):
        st.error("Updated Lawrence Quarters workbook not found in data_inputs.")
        return None

    quarters = {}
    for sheet_name in LAWRENCE_SHEETS:
        try:
            df = pd.read_excel(workbook_path, sheet_name=sheet_name, header=None)
        except Exception as e:
            st.error(f"Unable to read {sheet_name}: {e}")
            return None

        sections = {}
        for section_key, section_config in LAWRENCE_SECTION_CONFIG[sheet_name].items():
            sections[section_key] = parse_lawrence_section(df, section_config)
        quarters[sheet_name] = sections

    return quarters


def build_section_comparison_df(quarters, section_key):
    rows = []
    for sheet_name, sections in quarters.items():
        quarter_label = LAWRENCE_SHEET_LABELS[sheet_name]
        df = sections[section_key]
        for _, row in df.iterrows():
            rows.append({
                'Quarter': quarter_label,
                'Category': row['label'],
                'Count': row['count']
            })
    return pd.DataFrame(rows)

# Main content based on selection
if page == "Data Overview":
    st.markdown('<div class="section-header">Data Overview</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Lawrence 2026 Q1")
        st.write("DCF quarterly data with placement types, demographics, and permanency plans")
        lawrence_data = load_lawrence_data()
        if lawrence_data is not None:
            st.metric("Data Sections", len(lawrence_data))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Race by Town")
        st.write("Racial demographics across Massachusetts towns")
        race_data = load_race_data()
        if race_data is not None:
            st.metric("Towns", len(race_data.columns) - 1)
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("Student Discipline")
        st.write("School discipline statistics by student demographics")
        discipline_data = load_discipline_data()
        if discipline_data is not None:
            st.metric("Student Groups", len(discipline_data))
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Lawrence 2026 Q1 Dashboard":
    st.markdown('<div class="section-header">DCF Sections</div>', unsafe_allow_html=True)

    lawrence_quarters = load_lawrence_quarters()
    if lawrence_quarters is None:
        st.stop()

    tab_section, tab_full = st.tabs(["Section View", "Full Report"])

    with tab_section:
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_section = st.selectbox(
                "Select Section",
                list(SECTION_DISPLAY.keys()),
                format_func=lambda x: SECTION_DISPLAY[x]
            )
        with col2:
            show_data = st.checkbox("Show Raw Data", value=False)

        comparison_df = build_section_comparison_df(lawrence_quarters, selected_section)

        if show_data:
            st.subheader(f"Raw Data — {SECTION_DISPLAY[selected_section]}")
            st.dataframe(comparison_df, use_container_width=True)

        st.subheader(f"{SECTION_DISPLAY[selected_section]} Across Quarters")
        quarter_cols = st.columns(len(LAWRENCE_SHEETS))
        for idx, sheet_name in enumerate(LAWRENCE_SHEETS):
            quarter_label = LAWRENCE_SHEET_LABELS[sheet_name]
            section_df = lawrence_quarters[sheet_name][selected_section]
            with quarter_cols[idx]:
                st.markdown(f"**{quarter_label}**")
                if selected_section in ['race_in_placement', 'primary_language_in_placement']:
                    fig = px.pie(
                        section_df,
                        values='count',
                        names='label',
                        title=quarter_label
                    )
                else:
                    fig = px.bar(
                        section_df,
                        x='label',
                        y='count',
                        title=quarter_label,
                        color='label',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        st.markdown('---')
        st.subheader('Change Over Quarters')
        if not comparison_df.empty:
            trend_fig = px.line(
                comparison_df,
                x='Quarter',
                y='Count',
                color='Category',
                markers=True,
                title=f"{SECTION_DISPLAY[selected_section]} Trend Across Quarters"
            )
            st.plotly_chart(trend_fig, use_container_width=True)

            bar_fig = px.bar(
                comparison_df,
                x='Category',
                y='Count',
                color='Quarter',
                barmode='group',
                title=f"{SECTION_DISPLAY[selected_section]} Comparison Across Quarters"
            )
            bar_fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(bar_fig, use_container_width=True)

    with tab_full:
        selected_quarter = st.selectbox(
            "Select Quarter",
            LAWRENCE_SHEETS,
            format_func=lambda x: LAWRENCE_SHEET_LABELS[x],
            key='full_report_quarter'
        )

        st.subheader(f"Full Report — {LAWRENCE_SHEET_LABELS[selected_quarter]}")
        full_report = lawrence_quarters[selected_quarter]

        for section_key in SECTION_DISPLAY:
            section_df = full_report[section_key]
            st.markdown(f"### {SECTION_DISPLAY[section_key]}")
            if not section_df.empty:
                if section_key in ['race_in_placement', 'primary_language_in_placement']:
                    fig = px.pie(
                        section_df,
                        values='count',
                        names='label',
                        title=SECTION_DISPLAY[section_key]
                    )
                else:
                    fig = px.bar(
                        section_df,
                        x='label',
                        y='count',
                        title=SECTION_DISPLAY[section_key],
                        color='label',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

elif page == "Race by Town Demographics":
    st.markdown('<div class="section-header">Race by Town Demographics</div>', unsafe_allow_html=True)

    race_data = load_race_data()
    if race_data is None:
        st.stop()

    # Interactive controls
    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox("Chart Type", ["Pie Charts", "Bar Charts", "Heatmap"])
    with col2:
        selected_towns = st.multiselect("Select Towns",
                                       [col for col in race_data.columns if col not in ['Demographic', 'United States']],
                                       default=['North Andover', 'Methuen', 'Lawrence'])

    if chart_type == "Pie Charts":
        st.subheader("Racial Distribution by Town (Pie Charts)")

        # Create pie charts for selected towns
        cols = st.columns(min(len(selected_towns), 3))
        for i, town in enumerate(selected_towns):
            with cols[i % 3]:
                town_data = race_data[['Demographic', town]].copy()
                town_data = town_data[town_data[town] > 0]  # Filter out zero values

                fig = px.pie(town_data, values=town, names='Demographic',
                           title=f"{town} Racial Distribution")
                st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Bar Charts":
        st.subheader("Racial Distribution by Town (Bar Charts)")

        # Prepare data for grouped bar chart
        plot_data = race_data.melt(id_vars='Demographic',
                                  value_vars=selected_towns,
                                  var_name='Town',
                                  value_name='Percentage')

        fig = px.bar(plot_data, x='Demographic', y='Percentage', color='Town',
                    title="Racial Distribution Comparison",
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Heatmap":
        st.subheader("Racial Distribution Heatmap")

        # Create heatmap
        heatmap_data = race_data.set_index('Demographic')[selected_towns]

        fig = px.imshow(heatmap_data,
                       title="Racial Distribution Heatmap",
                       color_continuous_scale='Blues',
                       aspect='auto')
        fig.update_layout(
            xaxis_title="Town",
            yaxis_title="Demographic Group"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Show raw data
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Demographic Data")
        st.dataframe(race_data, use_container_width=True)

elif page == "Student Discipline Data":
    st.markdown('<div class="section-header">Student Discipline Statistics</div>', unsafe_allow_html=True)

    discipline_data = load_discipline_data()
    if discipline_data is None:
        st.stop()

    # Interactive controls
    col1, col2 = st.columns(2)
    with col1:
        viz_type = st.selectbox("Visualization Type", ["Bar Charts", "Pie Charts", "Comparison Matrix"])
    with col2:
        selected_groups = st.multiselect("Select Student Groups",
                                        discipline_data['Student Group'].unique(),
                                        default=discipline_data['Student Group'].unique()[:5])

    # Filter data
    filtered_discipline = discipline_data[discipline_data['Student Group'].isin(selected_groups)]

    discipline_cols = [col for col in discipline_data.columns if col.startswith('%')]

    if viz_type == "Bar Charts":
        st.subheader("Discipline Rates by Student Group")

        # Create subplots for each discipline type
        fig = make_subplots(rows=2, cols=4,
                           subplot_titles=[col.replace('% ', '') for col in discipline_cols],
                           vertical_spacing=0.1)

        for i, col in enumerate(discipline_cols):
            row = i // 4 + 1
            col_pos = i % 4 + 1

            fig.add_trace(
                go.Bar(x=filtered_discipline['Student Group'],
                      y=filtered_discipline[col],
                      name=col.replace('% ', ''),
                      showlegend=False),
                row=row, col=col_pos
            )

            fig.update_xaxes(tickangle=-45, row=row, col=col_pos)

        fig.update_layout(height=800, title_text="Student Discipline Rates by Category")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "Pie Charts":
        st.subheader("Discipline Type Distribution by Student Group")

        # Create pie charts for selected groups
        cols = st.columns(min(len(selected_groups), 3))
        for i, group in enumerate(selected_groups):
            with cols[i % 3]:
                group_data = filtered_discipline[filtered_discipline['Student Group'] == group]
                if len(group_data) > 0:
                    discipline_values = group_data[discipline_cols].iloc[0]
                    non_zero = discipline_values[discipline_values > 0]

                    if len(non_zero) > 0:
                        fig = px.pie(values=non_zero.values,
                                   names=[col.replace('% ', '') for col in non_zero.index],
                                   title=f"{group} Discipline Distribution")
                        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "Comparison Matrix":
        st.subheader("Discipline Rate Comparison Matrix")

        # Create a matrix view
        matrix_data = filtered_discipline.set_index('Student Group')[discipline_cols]

        fig = px.imshow(matrix_data.T,
                       title="Discipline Rates Matrix",
                       color_continuous_scale='Reds',
                       aspect='auto')
        fig.update_layout(
            xaxis_title="Student Group",
            yaxis_title="Discipline Type"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Students", f"{filtered_discipline['Students'].sum():,}")

    with col2:
        st.metric("Students Disciplined", f"{filtered_discipline['Students Disciplined'].sum():.0f}")

    with col3:
        avg_in_school = filtered_discipline['% In-School Suspension'].mean()
        st.metric("Avg In-School Suspension", f"{avg_in_school:.1f}%")

    with col4:
        avg_out_school = filtered_discipline['% Out-of-School Suspension'].mean()
        st.metric("Avg Out-of-School Suspension", f"{avg_out_school:.1f}%")

    # Show raw data
    if st.checkbox("Show Raw Data"):
        st.subheader("Raw Discipline Data")
        st.dataframe(filtered_discipline, use_container_width=True)
