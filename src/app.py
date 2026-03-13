import dash
from dash import dcc, html, Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
import warnings

# 1. DISABLE ALTAIR ROW LIMIT & WARNINGS
alt.data_transformers.disable_max_rows()
warnings.filterwarnings("ignore")

# =============================================================================
# 2. DATA LOADING & PRE-PROCESSING 
# =============================================================================
try:
    print("Loading database.csv...")
    impacts = pd.read_csv("../data/database.csv", low_memory=False)
except FileNotFoundError:
    print("Error: database.csv not found.")
    impacts = pd.DataFrame()

# Extract Date and Month
impacts['Incident Date'] = pd.to_datetime(dict(
    year=impacts['Incident Year'], 
    month=impacts['Incident Month'], 
    day=impacts['Incident Day']
), errors='coerce')
impacts['Month'] = impacts['Incident Date'].dt.strftime('%b').fillna('Unknown')

# Unit Conversions & Missing Values
impacts['Height'] = pd.to_numeric(impacts['Height'], errors='coerce').fillna(0).divide(3.28084) # ft to m
impacts['Speed'] = pd.to_numeric(impacts['Speed'], errors='coerce').fillna(0).multiply(1.852) # knots to km/h

# Apply Log Transformations (log1p handles 0s safely)
impacts['Log_Height'] = np.log1p(impacts['Height'])
impacts['Log_Speed'] = np.log1p(impacts['Speed'])

impacts['Aircraft Damage'] = pd.to_numeric(impacts['Aircraft Damage'], errors='coerce').fillna(0)
impacts["Fatalities"] = pd.to_numeric(impacts["Fatalities"], errors='coerce').fillna(0)
impacts["Injuries"] = pd.to_numeric(impacts["Injuries"], errors='coerce').fillna(0)

impacts["Flight Phase"] = impacts["Flight Phase"].fillna("UNKNOWN")
impacts["Species Name"] = impacts["Species Name"].fillna("UNKNOWN BIRD")
impacts["Aircraft Type"] = impacts.get("Aircraft Type", pd.Series(dtype=str)).fillna("Unknown")
impacts["State"] = impacts.get("State", pd.Series(dtype=str)).fillna("Unknown")

# Dictionary to map 2-letter state abbreviations to IDs for the Vega US Map
STATE_IDS = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10, 'DC': 11, 'FL': 12, 
    'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19, 'KS': 20, 'KY': 21, 'LA': 22, 
    'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28, 'MO': 29, 'MT': 30, 'NE': 31, 
    'NV': 32, 'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39, 'OK': 40, 
    'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46, 'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50, 
    'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55, 'WY': 56
}
impacts['state_id'] = impacts['State'].map(STATE_IDS)

TOTAL_RECORDS = len(impacts)

# =============================================================================
# 3. APP SETUP & LAYOUT
# =============================================================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Wildlife Strikes"

# Use vh (viewport height) overflow hidden to strictly prevent full-page scrolling
app.layout = dbc.Container([
    # --- Top Header & Key Statistics ---
    dbc.Row([
        dbc.Col([
            html.H3("FAA Aircraft Wildlife Strikes", className="fw-bold mt-1 text-primary"),
            html.P([
                "Interactive analysis of flight-animal impacts. ",
                html.Span("*Note: 2015 data is up to September.", className="text-danger fw-bold")
            ], className="text-muted mb-1 small")
        ], width=4),
        
        dbc.Col([
            dbc.Card(
                dbc.CardBody(
                    dbc.Row([
                        dbc.Col([html.Small("Total Records", className="text-muted text-uppercase fw-bold"), html.H5(f"{TOTAL_RECORDS:,}", className="text-primary fw-bold mb-0")]),
                        dbc.Col([html.Small("Incidents", className="text-muted text-uppercase fw-bold"), html.H5(id='stat-incidents', className="text-primary fw-bold mb-0")]),
                        dbc.Col([html.Small("With Damage", className="text-muted text-uppercase fw-bold"), html.H5(id='stat-damage', className="text-danger fw-bold mb-0")]),
                        dbc.Col([html.Small("Injuries", className="text-muted text-uppercase fw-bold"), html.H5(id='stat-injuries', className="text-warning fw-bold mb-0")]),
                        dbc.Col([html.Small("Fatalities", className="text-muted text-uppercase fw-bold"), html.H5(id='stat-fatalities', className="text-dark fw-bold mb-0")]),
                    ], className="text-center")
                ), className="mt-1 border-0 shadow-sm"
            )
        ], width=8)
    ], className="mb-2"),

    dbc.Row([
        # --- Sidebar ---
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Filters & Controls", className="fw-bold border-bottom pb-2 mb-2 text-primary"),
                    
                    html.Label("Impact Severity:", className="fw-bold small text-muted mb-0"),
                    dcc.Dropdown(
                        id='outcome-filter',
                        options=[
                            {'label': 'All Impacts', 'value': 'all'},
                            {'label': 'Damage', 'value': 'damage'},
                            {'label': 'Injuries', 'value': 'injury'},
                            {'label': 'Death', 'value': 'death'}
                        ],
                        value='all',
                        clearable=False,
                        className="mb-2 shadow-sm"
                    ),
                    
                    html.Label("Distribution Metric (Log):", className="fw-bold small text-muted mb-0"),
                    dcc.Dropdown(
                        id='panel-c-filter',
                        options=[
                            {'label': 'Log(Impact Speed)', 'value': 'Log_Speed'},
                            {'label': 'Log(Impact Height)', 'value': 'Log_Height'}
                        ],
                        value='Log_Speed',
                        clearable=False,
                        className="mb-2 shadow-sm"
                    ),

                    html.Label("Breakdown Category:", className="fw-bold small text-muted mb-0"),
                    dcc.Dropdown(
                        id='breakdown-filter',
                        options=[
                            {'label': 'Flight Phase', 'value': 'Flight Phase'},
                            {'label': 'Aircraft Type', 'value': 'Aircraft Type'},
                            {'label': 'Month', 'value': 'Month'}
                        ],
                        value='Flight Phase',
                        clearable=False,
                        className="mb-3 shadow-sm"
                    ),
                    
                    dbc.Button(
                        "Reset Filters & Charts", 
                        id="reset-btn", 
                        color="secondary", 
                        outline=True, 
                        className="w-100 mb-3 shadow-sm fw-bold",
                        size="sm"
                    ),

                    # --- Information Accordion ---
                    dbc.Accordion([
                        dbc.AccordionItem([
                            html.Ul([
                                html.Li("Click bars to filter elements.", className="small"),
                                html.Li("Drag on Yearly Trend to filter years.", className="small"),
                                html.Li("Hover/Click Map to isolate states.", className="small")
                            ], className="ps-3 mb-0")
                        ], title="Interaction Guide"),
                    ], start_collapsed=True, className="mb-3 shadow-sm"),

                    # --- Dynamic Insights Box ---
                    html.Div([
                        html.Strong("Dynamic Insight", className="small text-primary d-block"),
                        html.Span(id='dynamic-insight', className="small text-dark", style={"fontStyle": "italic", "fontSize": "0.85rem"})
                    ], className="bg-light p-2 rounded mb-2 border-start border-4 border-primary shadow-sm"),

                    # --- Data Source Footer ---
                    html.Div([
                        html.Small("Data Source: FAA Wildlife Strike Database", className="text-muted text-center d-block", style={"fontSize": "0.75rem"}),
                        html.Small("Analysis & Dashboard by Student", className="text-muted text-center d-block", style={"fontSize": "0.75rem"})
                    ], className="mt-auto border-top pt-2")

                ], className="d-flex flex-column h-100 p-3")
            ], className="border-0 shadow-sm", style={'height': '75vh', 'overflowY': 'auto'})
        ], width=3),

        # --- Main Charts Area ---
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.Iframe(
                        id='main-plot',
                        style={'border-width': '0', 'width': '100%', 'height': '75vh'} 
                    )
                ], className="p-1")
            ], className="border-0 shadow-sm h-100")
        ], width=9)
    ])
], fluid=True, className="bg-light p-3", style={"height": "100vh", "overflow": "hidden"}) 

# =============================================================================
# 4. CALLBACKS
# =============================================================================

@app.callback(
    [Output('outcome-filter', 'value'),
     Output('panel-c-filter', 'value'),
     Output('breakdown-filter', 'value')],
    [Input('reset-btn', 'n_clicks')],
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """
    Resets the dashboard filters to their default values.

    This function is triggered by clicking the "Reset Filters & Charts" button.
    It returns the default string values for the three main dropdown menus, 
    which subsequently triggers the main dashboard update callback to clear 
    any active Altair brushes or selections.

    Parameters
    ----------
    n_clicks : int
        The number of times the reset button has been clicked.

    Returns
    -------
    tuple of str
        A tuple containing the default values for the dropdowns:
        ('all', 'Log_Speed', 'Flight Phase').
    """
    return 'all', 'Log_Speed', 'Flight Phase'


@app.callback(
    [Output('main-plot', 'srcDoc'),
     Output('stat-incidents', 'children'),
     Output('stat-damage', 'children'),
     Output('stat-injuries', 'children'),
     Output('stat-fatalities', 'children'),
     Output('dynamic-insight', 'children')],
    [Input('outcome-filter', 'value'),
     Input('panel-c-filter', 'value'),
     Input('breakdown-filter', 'value')]
)
def update_dashboard(severity, panel_c_col, panel_d_col):
    """
    Filters the FAA Wildlife Strike dataset and generates the interactive 
    Altair visualizations and dynamic KPI texts.

    Parameters
    ----------
    severity : str
        The severity level to filter the dataset by. 
        Valid options are 'all', 'damage', 'injury', or 'death'.
    panel_c_col : str
        The continuous metric to display in the logarithmic distribution 
        histogram. Valid options are 'Log_Speed' or 'Log_Height'.
    panel_d_col : str
        The categorical feature to group by in the breakdown bar chart. 
        Valid options are 'Flight Phase', 'Aircraft Type', or 'Month'.

    Returns
    -------
    tuple
        A 6-element tuple containing:
        - final_chart.to_html() (str): The compiled 2x3 Altair dashboard as an HTML string.
        - stat_incidents (str): Formatted total number of incidents.
        - stat_damage (str): Formatted total number of incidents with damage.
        - stat_injuries (str): Formatted total number of injuries.
        - stat_fatalities (str): Formatted total number of fatalities.
        - insight_text (str): A dynamically generated string summarizing the top species and max speed.
    """
    df = impacts.copy()
    
    if severity == 'damage':
        df = df[df['Aircraft Damage'] > 0]
    elif severity == 'injury':
        df = df[df['Injuries'] > 0]
    elif severity == 'death':
        df = df[df['Fatalities'] > 0]

    stat_incidents = f"{len(df):,}"
    stat_damage = f"{int(df['Aircraft Damage'].sum()):,}"
    stat_injuries = f"{int(df['Injuries'].sum()):,}"
    stat_fatalities = f"{int(df['Fatalities'].sum()):,}"

    df_chart = df[~df['Species Name'].str.contains('UNK', case=False, na=False)]
    
    if len(df_chart) == 0:
        return "<h3>No data available for this filter.</h3>", stat_incidents, stat_damage, stat_injuries, stat_fatalities, "No incidents match the current filter criteria."

    top_species = df_chart['Species Name'].value_counts().head(10).index.tolist()
    df_chart_species = df_chart[df_chart['Species Name'].isin(top_species)]
    state_counts = df_chart.groupby(['State', 'state_id']).size().reset_index(name='incidents')

    most_common = top_species[0].title() if top_species else "Unknown"
    max_speed = int(df_chart['Speed'].max()) if not df_chart['Speed'].isna().all() else 0
    insight_text = f"Top species involved: {most_common}. Max speed recorded: {max_speed:,} km/h."

    # ================= ALTAIR SELECTIONS & SIZING =================
    # SCALED UP DIMENSIONS
    CHART_WIDTH = 280
    CHART_HEIGHT = 190

    click_species = alt.selection_point(fields=['Species Name'])
    brush_year = alt.selection_interval(encodings=['x'])
    map_click = alt.selection_point(fields=['State'])
    bar_hover = alt.selection_point(fields=['State'], on='mouseover', nearest=True)

    # ---------------- ROW 1 CHARTS ----------------
    
    base_trend = alt.Chart(df_chart_species).mark_line(point=True).encode(
        x=alt.X('Incident Year:Q', 
                title='Year', 
                scale=alt.Scale(zero=False), 
                axis=alt.Axis(format='d', tickCount=5, tickMinStep=1, labelAngle=0)),
        y=alt.Y('count()', title='Incidents'),
        color=alt.value('#2c3e50'),
        tooltip=['Incident Year', 'count()']
    ).add_params(brush_year).transform_filter(click_species)

    year_range_text = alt.Chart(df_chart_species).mark_text(
        align='left', baseline='top', dx=5, dy=5, fontSize=10, color='gray'
    ).encode(
        x=alt.value(0), y=alt.value(0), text=alt.Text('label:N')
    ).transform_filter(brush_year).transform_aggregate(
        min_yr='min(Incident Year)', max_yr='max(Incident Year)'
    ).transform_calculate(
        label='"Selected: " + datum.min_yr + "-" + datum.max_yr'
    )
    
    chart_trend = (base_trend + year_range_text).properties(
        title=alt.TitleParams(text='Yearly Trend', subtitle='*2015 partial', subtitleColor='red'),
        width=CHART_WIDTH, height=CHART_HEIGHT
    )

    us_states = alt.topo_feature(data.us_10m.url, 'states')
    choropleth = alt.Chart(us_states).mark_geoshape().transform_lookup(
        lookup='id', from_=alt.LookupData(state_counts, 'state_id', ['incidents', 'State'])
    ).encode(
        color=alt.Color('incidents:Q', title='Incidents', scale=alt.Scale(scheme='blues')),
        stroke=alt.condition(bar_hover, alt.value('black'), alt.value('white')),
        strokeWidth=alt.condition(bar_hover, alt.value(2), alt.value(0.5)),
        opacity=alt.condition(map_click, alt.value(1), alt.value(0.3)),
        tooltip=['State:N', 'incidents:Q']
    ).add_params(map_click).project(type='albersUsa').properties(
        title='Geographic Distribution', width=CHART_WIDTH, height=CHART_HEIGHT
    )

    chart_species = alt.Chart(df_chart_species).mark_bar().encode(
        y=alt.Y('Species Name:N', sort='-x', title='Species'),
        x=alt.X('count()', title='Incidents'),
        color=alt.condition(click_species, alt.Color('Species Name:N', legend=None), alt.value('lightgray')),
        tooltip=['Species Name', 'count()']
    ).add_params(click_species).transform_filter(brush_year).properties(
        title='Top 10 Species', width=CHART_WIDTH, height=CHART_HEIGHT
    )

    # ---------------- ROW 2 CHARTS ----------------
    orig_col = "Speed (km/h)" if "Speed" in panel_c_col else "Height (m)"
    chart_dist = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X(f'{panel_c_col}:Q', bin=alt.Bin(maxbins=30), title=f'Log of {orig_col}'),
        y=alt.Y('count()', title='Frequency'),
        color=alt.value('teal'),
        tooltip=[alt.Tooltip(f'{panel_c_col}:Q', bin=True, title='Log Range'), 'count()']
    ).transform_filter(click_species).transform_filter(brush_year).properties(
        title=f'{orig_col} Distribution', width=CHART_WIDTH, height=CHART_HEIGHT
    )

    state_bars = alt.Chart(state_counts.nlargest(10, 'incidents')).mark_bar().encode(
        x=alt.X('incidents:Q', title='Incidents'),
        y=alt.Y('State:N', sort='-x', title='State'),
        color=alt.Color('incidents:Q', legend=None, scale=alt.Scale(scheme='blues')),
        stroke=alt.condition(bar_hover, alt.value('black'), alt.value('#ffffff00'))
    ).add_params(bar_hover).transform_filter(map_click).properties(
        title='Top 10 States', width=CHART_WIDTH, height=CHART_HEIGHT
    )

    sort_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Unknown'] if panel_d_col == 'Month' else '-x'
    chart_breakdown = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('count:Q', title='Incidents'),
        y=alt.Y(panel_d_col, sort=sort_order, title=panel_d_col, axis=alt.Axis(labelAngle=0)),
        color=alt.Color(f'{panel_d_col}:N', legend=None, scale=alt.Scale(scheme='set2')),
        tooltip=[panel_d_col, 'count:Q']
    ).transform_filter(click_species).transform_filter(brush_year).transform_aggregate(
        count='count()', groupby=[panel_d_col]
    ).transform_window(
        rank='rank(count)', sort=[alt.SortField('count', order='descending')]
    ).transform_filter(alt.datum.rank <= 10).properties(
        title=f'Breakdown by {panel_d_col}', width=CHART_WIDTH, height=CHART_HEIGHT
    )

    # ================= COMBINE DASHBOARD INTO 2 ROWS OF 3 =================
    row1 = chart_trend | choropleth | chart_species
    row2 = chart_dist | state_bars | chart_breakdown
    
    final_chart = (row1 & row2).resolve_scale(
        color='independent'
    ).configure_concat(
        spacing=15 # Tightened up slightly to fit the larger charts nicely
    ).configure_view(
        strokeOpacity=0
    ).configure_axis(
        labelFontSize=10, titleFontSize=11 
    ).configure_title(
        fontSize=12, anchor='start'
    )
    
    return final_chart.to_html(), stat_incidents, stat_damage, stat_injuries, stat_fatalities, insight_text

if __name__ == '__main__':
    app.run(debug=False)