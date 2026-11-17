import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. GENERATE DATA
# ==========================================
np.random.seed(42)
dates = pd.date_range(start="2023-10-01", periods=30)
data = {
    "Date": dates,
    "Sleep_Duration_Hours": np.round(np.random.normal(7, 1.5, 30), 1),
    "Dream_Type": np.random.choice(["Lucid", "Nightmare", "Normal", "None"], 30, p=[0.15, 0.15, 0.5, 0.2]),
    "Morning_Mood_Score": np.random.randint(1, 11, 30),
    "Deep_Sleep_Percentage": np.random.randint(15, 45, 30)
}
df = pd.DataFrame(data)

# ==========================================
# 2. SEPARATE FUNCTIONS FOR EACH CHART
# ==========================================
_COLORS = ["#4C78A8", "#F58518", "#E45756", "#72B7B2"] 
BACKGROUND_COLOR = "#1E1E1E"

def create_line_chart(filtered_df):
    fig = px.line(filtered_df, x="Date", y="Morning_Mood_Score", markers=True,
                  title="Morning Mood Over Time", template="plotly_dark")
    fig.update_traces(line_color="#72B7B2", marker=dict(size=8, color="#72B7B2"))
    fig.update_layout(paper_bgcolor=BACKGROUND_COLOR, plot_bgcolor=BACKGROUND_COLOR, font=dict(color="#D3D3D3"))
    return fig

def create_donut_chart(filtered_df):
    dream_counts = filtered_df["Dream_Type"].value_counts().reset_index()
    dream_counts.columns = ["Dream_Type", "Count"]
    fig = px.pie(dream_counts, values="Count", names="Dream_Type", hole=0.4,
                 title="Dream Types Distribution", template="plotly_dark",
                 color_discrete_sequence=DISCRETE_COLORS)
    fig.update_layout(paper_bgcolor=BACKGROUND_COLOR, font=dict(color="#D3D3D3"))
    return fig

def create_scatter_chart(filtered_df):
    fig = px.scatter(filtered_df, x="Sleep_Duration_Hours", y="Morning_Mood_Score",
                     size="Deep_Sleep_Percentage", color="Morning_Mood_Score",
                     title="Sleep vs Mood", template="plotly_dark",
                     color_continuous_scale=px.colors.sequential.Blues, size_max=20)
    fig.update_traces(marker=dict(line=dict(width=0.5, color='white')))
    fig.update_layout(paper_bgcolor=BACKGROUND_COLOR, plot_bgcolor=BACKGROUND_COLOR, font=dict(color="#D3D3D3"))
    return fig

def create_heatmap_chart(filtered_df):
    num_cols = filtered_df[['Sleep_Duration_Hours', 'Morning_Mood_Score', 'Deep_Sleep_Percentage']]
    fig = px.imshow(num_cols.corr(), text_auto=True, aspect="auto",
                    title="Correlation Matrix", color_continuous_scale="Teal",
                    template="plotly_dark")
    fig.update_layout(paper_bgcolor=BACKGROUND_COLOR, plot_bgcolor=BACKGROUND_COLOR, font=dict(color="#D3D3D3"))
    return fig

# ==========================================
# 3. DASHBOARD STRUCTURE (LAYOUT)
# ==========================================
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Quantum Dream Analysis Dashboard", style={'color': '#D3D3D3', 'textAlign': 'center', 'fontFamily': 'sans-serif'}),

    # Filtros
    html.Div([
        html.Div([
            html.Label("Filter by Dream Type:", style={'color': '#D3D3D3'}),
            dcc.Dropdown(
                id="filter-dream-bj",
                options=[{'label': 'All', 'value': 'All'}] + [{'label': k, 'value': k} for k in df['Dream_Type'].unique()],
                value='All',
                style={'color': 'black'}
            ),
        ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Min Sleep Hours:", style={'color': '#D3D3D3'}),
            dcc.Slider(
                id="filter-sleep-bj",
                min=4.0, max=10.0, step=0.5, value=4.0,
                marks={i: str(i) for i in range(4, 11)}
            )
        ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
    ]),

    
    dcc.Tabs(id="tabs-bj", value="tab-overview-bj", children=[
        dcc.Tab(label="Overview & Distribution", value="tab-overview-bj"),
        dcc.Tab(label="Correlations", value="tab-correlations-bj")
    ]),

    html.Div(id="tab-content-bj", style={"padding": "20px"})
], style={'backgroundColor': BACKGROUND_COLOR, 'minHeight': '100vh', 'padding': '20px'})

# ==========================================
# 4. CALLBACKS
# ==========================================
@app.callback(
    Output("tab-content-bj", "children"),
    [Input("tabs-bj", "value"),
     Input("filter-dream-bj", "value"),
     Input("filter-sleep-bj", "value")]
)
def render_content(active_tab, selected_dream, min_sleep):
    dff = df[df['Sleep_Duration_Hours'] >= min_sleep]
    if selected_dream != "All":
        dff = dff[dff['Dream_Type'] == selected_dream]

    if dff.empty:
        return html.Div("No data available for these filters.", style={'color': '#D3D3D3', 'textAlign': 'center'})

    if active_tab == "tab-overview-bj":
        fig1 = create_line_chart(dff)
        fig2 = create_donut_chart(dff)
        return html.Div([
            html.Div(dcc.Graph(figure=fig1), style={"width": "50%", "display": "inline-block"}),
            html.Div(dcc.Graph(figure=fig2), style={"width": "50%", "display": "inline-block"})
        ])
    elif active_tab == "tab-correlations-bj":
        fig3 = create_scatter_chart(dff)
        if len(dff) > 1:
            fig4 = create_heatmap_chart(dff)
            return html.Div([
                html.Div(dcc.Graph(figure=fig3), style={"width": "50%", "display": "inline-block"}),
                html.Div(dcc.Graph(figure=fig4), style={"width": "50%", "display": "inline-block"})
            ])
        else:
            return html.Div(dcc.Graph(figure=fig3), style={"width": "100%"})

if __name__ == '__main__':
    app.run(debug=True)