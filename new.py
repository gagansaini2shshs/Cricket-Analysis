import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')
from streamlit_echarts import st_echarts
    


# Set page config
st.set_page_config(
    page_title="IPL Analysis Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .tab-header {
        font-size: 1.5rem;
        color: #2E86C1;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF6B35;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 10px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF6B35;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the datasets"""
    try:
        # You would replace these with your actual file paths
        matches_df = pd.read_csv('new_Cleaned_IPL_Matches_2008_2022.csv')
        balls_df = pd.read_csv('new1_Cleaned_IPL_Ball_By_Ball_2008_2022.csv')
        
        # Data preprocessing
        matches_df['Date'] = pd.to_datetime(matches_df['Date'])
        matches_df['Year'] = matches_df['Date'].dt.year
        
        return matches_df, balls_df
    except FileNotFoundError:
        st.error("Please upload the IPL datasets (IPL_Matches_2008_2021.csv and IPL_Ball_by_Ball_2008_2021.csv)")
        return None, None



def main():
    st.markdown('<h1 class="main-header">🏏 IPL Analysis Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    matches_df, balls_df = load_data()
    
    
    # Sidebar
    st.sidebar.markdown("## 🏏 IPL Dashboard")
    st.sidebar.markdown("---")
    # New checkbox to include/exclude "No Result" matches
    include_no_result = st.sidebar.checkbox("Include 'No Result' Matches", value=False)

    if not include_no_result:
        matches_df = matches_df[matches_df['WinningTeam'] != 'No Result']

    
    # Dataset overview in sidebar
    st.sidebar.markdown("### Dataset Overview")
    st.sidebar.metric("Total Matches", len(matches_df))
    st.sidebar.metric("Total Deliveries", len(balls_df))
    st.sidebar.metric("Seasons", f"{matches_df['Season'].min()} - {matches_df['Season'].max()}")
    
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏆 Team Analysis", "👥 Player Performance", "🎯 Match Insights", 
        "🏟️ Venue Analysis", "📊 Season Trends", "🔢 Statistical Overview"
    ])
    
    with tab1:
        team_analysis_tab(matches_df, balls_df)
    
    with tab2:
        player_performance_tab(matches_df, balls_df)
    
    with tab3:
        match_insights_tab(matches_df, balls_df)
    
    with tab4:
        venue_analysis_tab(matches_df, balls_df)
    
    with tab5:
        season_trends_tab(matches_df, balls_df)
    
    with tab6:
        statistical_overview_tab(matches_df, balls_df)

def team_analysis_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">🏆 Team Performance Analysis</h2>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
        # Team Win Percentage
    team_wins = matches_df['WinningTeam'].value_counts()
    team_matches = matches_df['Team1'].value_counts() + matches_df['Team2'].value_counts()
    win_percentage = (team_wins / team_matches * 100).round(2)
        
    fig1 = px.bar(x=win_percentage.index, y=win_percentage.values,
                     title="Team Win Percentage",
                     labels={'x': 'Teams', 'y': 'Win Percentage'},
                     color=win_percentage.values,
                     color_continuous_scale='RdYlBu_r')
    fig1.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)
    
    # with col2:
        # Toss vs Match Win Analysis
    toss_match_win = matches_df[matches_df['TossWinner'] == matches_df['WinningTeam']].shape[0]
    total_matches = matches_df.shape[0]
    toss_win_percentage = (toss_match_win / total_matches) * 100

    # Create ECharts pie chart with simplified labels
    option = {
        "title": {
            "text": "Impact of Toss on Match Result",
            "left": "center"
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{a} <br/>{b}: {c}% ({d}%)"
        },
        "series": [
            {
                "name": "Toss Impact",
                "type": "pie",
                "radius": ["50%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}"  # Only show the category name, no percentage
                },
                "emphasis": {
                    "label": {
                        "show": True,
                        "formatter": "{b}: {d}%"  # Show percentage on hover only
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": [
                    {"value": toss_win_percentage, "name": "Toss Winner Won"},
                    {"value": 100 - toss_win_percentage, "name": "Toss Winner Lost"}
                ]
            }
        ]
    }

    # Display the chart in Streamlit
    st_echarts(
        options=option,
        height="400px",
        key="toss_impact_pie"
    )
        
    # col3, col4 = st.columns(2)
    
    # with col3:
        # Team Performance by Decision (Bat/Field First)
    decision_analysis = matches_df.groupby(['TossDecision', 'WinningTeam']).size().unstack(fill_value=0)
    fig3 = px.bar(decision_analysis.T, 
                     title="Wins by Toss Decision",
                     labels={'index': 'Teams', 'value': 'Number of Wins'},
                     barmode='group')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # with col4:
        # Head to Head Comparison
    st.subheader("Head-to-Head Comparison")
    teams = matches_df['Team1'].unique()
    team1 = st.selectbox("Select Team 1", teams, key="h2h_team1")
    team2 = st.selectbox("Select Team 2", [t for t in teams if t != team1], key="h2h_team2")
        
    h2h_matches = matches_df[((matches_df['Team1'] == team1) & (matches_df['Team2'] == team2)) |
                                ((matches_df['Team1'] == team2) & (matches_df['Team2'] == team1))]
        
    team1_wins = h2h_matches[h2h_matches['WinningTeam'] == team1].shape[0]
    team2_wins = h2h_matches[h2h_matches['WinningTeam'] == team2].shape[0]
        
    fig4 = go.Figure(data=[go.Bar(x=[team1, team2], y=[team1_wins, team2_wins],
                            marker_color=['#FF6B35', '#2E86C1'],width=[0.3,0.3])])
    fig4.update_layout(title=f"{team1} vs {team2} - Head to Head", height=400)
    st.plotly_chart(fig4, use_container_width=True)
    
    # Team Performance Trends Over Years with Year Selector
    st.subheader("Team Performance Trends Over Years")
    
    # Year selection controls
    col_year1, col_year2, col_year3 = st.columns([1, 1, 2])
    
    available_years = sorted(matches_df['Year'].unique())
    min_year = min(available_years)
    max_year = max(available_years)
    
    with col_year1:
        start_year = st.selectbox("Start Year", available_years, index=0, key="team_trends_start_year")
    
    with col_year2:
        end_year = st.selectbox("End Year", available_years, index=len(available_years)-1, key="team_trends_end_year")
    
    with col_year3:
        # Team selection for highlighting specific teams
        all_teams = sorted(matches_df['WinningTeam'].unique())
        selected_teams = st.multiselect(
            "Select Teams to Highlight (leave empty for all teams)", 
            all_teams, 
            key="team_trends_teams"
        )
    
    # Ensure start_year is not greater than end_year
    if start_year > end_year:
        st.warning("Start year should be less than or equal to end year. Adjusting automatically.")
        start_year, end_year = min(start_year, end_year), max(start_year, end_year)
    
    # Filter data based on selected year range
    filtered_matches = matches_df[(matches_df['Year'] >= start_year) & (matches_df['Year'] <= end_year)]
    
    if len(filtered_matches) == 0:
        st.warning("No data available for the selected year range.")
    else:
        # Calculate wins for filtered data
        yearly_wins = filtered_matches.groupby(['Year', 'WinningTeam']).size().unstack(fill_value=0)
        
        # If specific teams are selected, filter the data
        if selected_teams:
            # Only show selected teams, but keep all years in the range
            available_teams_in_data = [team for team in selected_teams if team in yearly_wins.columns]
            if available_teams_in_data:
                yearly_wins = yearly_wins[available_teams_in_data]
            else:
                st.warning("Selected teams have no data in the chosen year range.")
                yearly_wins = yearly_wins.iloc[:, :0]  # Empty dataframe
        
        if not yearly_wins.empty:
            # Create the line plot
            fig5 = px.line(yearly_wins.T, 
                          title=f"Team Wins from {start_year} to {end_year}",
                          labels={'index': 'Year', 'value': 'Number of Wins'},
                          markers=True)
            
            # Customize the plot
            fig5.update_layout(
                height=500,
                xaxis_title="Year",
                yaxis_title="Number of Wins",
                legend_title="Teams",
                hovermode='x unified'
            )
            
            # Add some styling
            fig5.update_traces(line=dict(width=3), marker=dict(size=8))
            
            st.plotly_chart(fig5, use_container_width=True)
            
            # Display summary statistics for the selected period
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                total_matches_filtered = len(filtered_matches)
                st.metric("Total Matches in Period", total_matches_filtered)
            
            with col_stats2:
                if not yearly_wins.empty:
                    avg_wins_per_year = yearly_wins.mean().mean()
                    st.metric("Avg Wins per Team per Year", f"{avg_wins_per_year:.1f}")
                else:
                    st.metric("Avg Wins per Team per Year", "N/A")
            
            with col_stats3:
                years_span = end_year - start_year + 1
                st.metric("Years Selected", years_span)
            
            # Show top performing team in the selected period
            if not yearly_wins.empty:
                total_wins_period = yearly_wins.sum().sort_values(ascending=False)
                if len(total_wins_period) > 0:
                    st.success(f"**Most successful team in {start_year}-{end_year}:** {total_wins_period.index[0]} ({total_wins_period.iloc[0]} wins)")
                    
                    # Show a mini table with team performance in selected period
                    st.subheader("Team Performance Summary for Selected Period")
                    summary_data = []
                    for team in total_wins_period.index:
                        team_matches_period = filtered_matches[
                            (filtered_matches['Team1'] == team) | (filtered_matches['Team2'] == team)
                        ]
                        team_wins_period = total_wins_period[team]
                        win_percentage_period = (team_wins_period / len(team_matches_period) * 100) if len(team_matches_period) > 0 else 0
                        
                        summary_data.append({
                            'Team': team,
                            'Matches Played': len(team_matches_period),
                            'Wins': int(team_wins_period),
                            'Win %': f"{win_percentage_period:.1f}%"
                        })
                    
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
        else:
            st.info("No win data available for the selected criteria.")
    
    # Additional year-wise analysis
    if st.checkbox("Show Year-wise Detailed Analysis", key="detailed_year_analysis"):
        st.subheader("Detailed Year-wise Breakdown")
        
        selected_analysis_year = st.selectbox(
            "Select a specific year for detailed analysis", 
            available_years, 
            index=len(available_years)-1,
            key="detailed_analysis_year"
        )
        
        year_data = matches_df[matches_df['Year'] == selected_analysis_year]
        
        if len(year_data) > 0:
            col_detail1, col_detail2 = st.columns(2)
            
            with col_detail1:
                # Wins in selected year
                year_wins = year_data['WinningTeam'].value_counts()
                fig_detail1 = px.bar(
                    x=year_wins.index, 
                    y=year_wins.values,
                    title=f"Team Wins in {selected_analysis_year}",
                    labels={'x': 'Teams', 'y': 'Wins'},
                    color=year_wins.values,
                    color_continuous_scale='viridis'
                )
                fig_detail1.update_layout(height=400)
                st.plotly_chart(fig_detail1, use_container_width=True)
            
            with col_detail2:
                # Win margins analysis for the year
                year_margins = year_data.groupby('WinningTeam')['Margin'].mean().sort_values(ascending=False)
                fig_detail2 = px.bar(
                    x=year_margins.index,
                    y=year_margins.values,
                    title=f"Average Victory Margin in {selected_analysis_year}",
                    labels={'x': 'Teams', 'y': 'Avg Margin'},
                    color=year_margins.values,
                    color_continuous_scale='Blues'
                )
                fig_detail2.update_layout(height=400)
                st.plotly_chart(fig_detail2, use_container_width=True)
        else:
            st.warning(f"No data available for {selected_analysis_year}")

def player_performance_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">👥 Player Performance Analysis</h2>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
        # Man of the Match Awards
    mom_counts = matches_df['Player_of_Match'].value_counts().head(15)
    fig1 = px.bar(x=mom_counts.values, y=mom_counts.index,
                     title="Top 15 Players - Man of the Match Awards",
                     labels={'x': 'Number of Awards', 'y': 'Players'},
                     orientation='h',
                     color=mom_counts.values,
                     color_continuous_scale='viridis')
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    # with col2:
        # Top Run Scorers
    batsman_runs = balls_df.groupby('batter')['batsman_run'].sum().sort_values(ascending=False).head(15)
    fig2 = px.bar(x=batsman_runs.index, y=batsman_runs.values,
                     title="Top 15 Run Scorers",
                     labels={'x': 'Batsmen', 'y': 'Total Runs'},
                     color=batsman_runs.values,
                     color_continuous_scale='Blues')
    fig2.update_xaxes(tickangle=45)
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    # col3, col4 = st.columns(2)
    
    # with col3:
        # Strike Rate Analysis (Top 10 batsmen with minimum deliveries)
    batsman_balls = balls_df.groupby('batter').size()
    batsman_runs_detailed = balls_df.groupby('batter')['batsman_run'].sum()
    strike_rates = (batsman_runs_detailed / batsman_balls * 100).round(2)
    qualified_sr = strike_rates[batsman_balls >= 50].sort_values(ascending=False).head(10)
        
    fig3 = px.bar(x=qualified_sr.index, y=qualified_sr.values,
                     title="Top 10 Strike Rates (Min 50 balls faced)",
                     labels={'x': 'Batsmen', 'y': 'Strike Rate'},
                     color=qualified_sr.values,
                     color_continuous_scale='Reds')
    fig3.update_xaxes(tickangle=45)
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # with col4:
        # Wicket Takers
    wicket_balls = balls_df[balls_df['isWicketDelivery'] == 1]
    bowler_wickets = wicket_balls['bowler'].value_counts().head(15)
    fig4 = px.bar(x=bowler_wickets.index, y=bowler_wickets.values,
                     title="Top 15 Wicket Takers",
                     labels={'x': 'Bowlers', 'y': 'Wickets'},
                     color=bowler_wickets.values,
                     color_continuous_scale='Greens')
    fig4.update_xaxes(tickangle=45)
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)
    
    # Boundary Analysis
    st.subheader("Boundary Analysis")
    col5, col6 = st.columns(2)
    
    # with col5:
        # Fours vs Sixes
    fours = balls_df[balls_df['batsman_run'] == 4].groupby('batter').size().sort_values(ascending=False).head(10)
    sixes = balls_df[balls_df['batsman_run'] == 6].groupby('batter').size().sort_values(ascending=False).head(10)
        
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(name='Fours', x=fours.index, y=fours.values, marker_color='lightblue'))
    fig5.add_trace(go.Bar(name='Sixes', x=sixes.index, y=sixes.values, marker_color='orange'))
    fig5.update_layout(title='Top Boundary Hitters (Fours vs Sixes)', barmode='group', height=400)
    fig5.update_xaxes(tickangle=45)
    st.plotly_chart(fig5, use_container_width=True)
    
    # with col6:
        # Economy Rate Analysis
    bowler_runs = balls_df.groupby('bowler')['total_run'].sum()
    bowler_balls_bowled = balls_df.groupby('bowler').size()
    economy_rates = (bowler_runs / bowler_balls_bowled * 6).round(2)
    qualified_economy = economy_rates[bowler_balls_bowled >= 100].sort_values().head(10)
        
    fig6 = px.bar(x=qualified_economy.index, y=qualified_economy.values,
                     title="Best Economy Rates (Min 100 balls bowled)",
                     labels={'x': 'Bowlers', 'y': 'Economy Rate'},
                     color=qualified_economy.values,
                     color_continuous_scale='RdYlBu')
    fig6.update_xaxes(tickangle=45)
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)

def match_insights_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">🎯 Match Insights</h2>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
        # Win by Runs vs Wickets


    # Assuming matches_df is your DataFrame
    win_type = matches_df['WonBy'].value_counts()

    # Convert to ECharts format
    chart_data = [{"value": int(count), "name": str(name)} for name, count in win_type.items()]

    # Full ECharts configuration
    option = {
        "title": {
            "text": "Match Results: Wins by Runs vs Wickets",
            "left": "center",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} matches ({d}%)"
        },
        "legend": {
            "orient": "horizontal",
            "bottom": 0,
            "data": [str(name) for name in win_type.index]
        },
        "series": [
            {
                "name": "Win Type",
                "type": "pie",
                "radius": ["40%", "70%"],  # Outer and inner radius (donut)
                "avoidLabelOverlap": True,
                "itemStyle": {
                    "borderRadius": 6,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b|{b}}\n{d}%",  # Name bold + percentage
                    "rich": {
                        "b": {
                            "fontWeight": "bold",
                            "lineHeight": 22
                        }
                    }
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                },
                "labelLine": {
                    "show": True
                },
                "data": chart_data
            }
        ],
        "color": ["#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE"]  # Color palette
    }

    # Display the chart
    st_echarts(
        options=option,
        height="500px",  # Slightly taller to accommodate legend
        key="win_type_donut"
    )

    # with col2:
        # Filter margin data
    runs_margins = matches_df[matches_df['WonBy'] == 'Runs']['Margin']
    wicket_margins = matches_df[matches_df['WonBy'] == 'Wickets']['Margin']

        # Create side-by-side subplots
    fig2 = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Victory Margins (Runs)", "Victory Margins (Wickets)")
        )

        # Runs Margin Histogram
    fig2.add_trace(
            go.Histogram(
                x=runs_margins,
                nbinsx=20,
                marker_color='rgba(99, 110, 250, 0.7)',
                name='Runs'
            ),
            row=1, col=1
        )

        # Wickets Margin Histogram
    fig2.add_trace(
            go.Histogram(
                x=wicket_margins,
                nbinsx=10,
                marker_color='rgba(239, 85, 59, 0.7)',
                name='Wickets'
            ),
            row=1, col=2
        )

        # Update layout
    fig2.update_layout(
            title_text='Distribution of Victory Margins (Runs vs Wickets)',
            height=400,
            showlegend=False,
            bargap=0.2
        )

        # X and Y axis titles
    fig2.update_xaxes(title_text="Run Margin", row=1, col=1)
    fig2.update_yaxes(title_text="Match Count", row=1, col=1)

    fig2.update_xaxes(title_text="Wicket Margin", row=1, col=2)
    fig2.update_yaxes(title_text="Match Count", row=1, col=2)

        # Show in Streamlit
    st.plotly_chart(fig2, use_container_width=True)

    # col3, col4 = st.columns(2)
    
    # with col3:
        # Runs scored in different overs
    over_runs = balls_df.groupby('overs')['total_run'].mean().round(2)
    fig3 = px.line(x=over_runs.index, y=over_runs.values,
                      title="Average Runs per Over",
                      labels={'x': 'Over Number', 'y': 'Average Runs'},
                      markers=True)
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # with col4:
        # Wickets in different overs
    over_wickets = balls_df[balls_df['isWicketDelivery'] == 1].groupby('overs').size()
    fig4 = px.bar(x=over_wickets.index, y=over_wickets.values,
                     title="Wickets Distribution by Over",
                     labels={'x': 'Over Number', 'y': 'Number of Wickets'},
                     color=over_wickets.values,
                     color_continuous_scale='Reds')
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)
    
    # # Close Match Analysis
    # st.subheader("Close Match Analysis")
    # close_matches_runs = matches_df[(matches_df['WonBy'] == 'Runs') & (matches_df['Margin'] <= 10)]
    # close_matches_wickets = matches_df[(matches_df['WonBy'] == 'Wickets') & (matches_df['Margin'] <= 2)]
    
    # col5, col6 = st.columns(2)
    
    # with col5:
    #     st.metric("Close Matches (≤10 runs)", len(close_matches_runs))
    #     if len(close_matches_runs) > 0:
    #         fig5 = px.histogram(close_matches_runs, x='Margin',
    #                            title="Distribution of Close Wins by Runs (≤10 runs)",
    #                            nbins=10)
    #         st.plotly_chart(fig5, use_container_width=True)
    
    # with col6:
    #     st.metric("Close Matches (≤2 wickets)", len(close_matches_wickets))
    #     if len(close_matches_wickets) > 0:
    #         fig6 = px.histogram(close_matches_wickets, x='Margin',
    #                            title="Distribution of Close Wins by Wickets (≤2 wickets)",
    #                            nbins=3)
    #         st.plotly_chart(fig6, use_container_width=True)

def venue_analysis_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">🏟️ Venue Analysis</h2>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
        # Matches per Venue
    venue_matches = matches_df['Venue'].value_counts().head(15)
    fig1 = px.bar(x=venue_matches.values, y=venue_matches.index,
                     title="Top 15 Venues by Number of Matches",
                     labels={'x': 'Number of Matches', 'y': 'Venues'},
                     orientation='h',
                     color=venue_matches.values,
                     color_continuous_scale='viridis')
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    # with col2:
        # Toss Decision by Venue
    venue_toss = matches_df.groupby(['Venue', 'TossDecision']).size().unstack(fill_value=0)
    venue_toss_pct = venue_toss.div(venue_toss.sum(axis=1), axis=0) * 100
    top_venues = venue_matches.head(10).index
    venue_toss_pct_top = venue_toss_pct.loc[top_venues]
        
    fig2 = px.bar(venue_toss_pct_top, 
                     title="Toss Decision Preference by Top Venues (%)",
                     labels={'index': 'Venues', 'value': 'Percentage'},
                     barmode='stack')
    fig2.update_xaxes(tickangle=45)
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    # col3, col4 = st.columns(2)
    
    # with col3:
        # Average runs per venue
    if 'Venue' in balls_df.columns:
            venue_runs = balls_df.groupby('Venue')['total_run'].mean().sort_values(ascending=False).head(10)
    else:
            # If venue info is not in balls_df, create sample data
            venues = matches_df['Venue'].unique()[:10]
            venue_runs = pd.Series(np.random.uniform(6, 9, len(venues)), index=venues).sort_values(ascending=False)
        
    fig3 = px.bar(x=venue_runs.index, y=venue_runs.values,
                     title="Highest Scoring Venues (Runs per ball)",
                     labels={'x': 'Venues', 'y': 'Average Runs per Ball'},
                     color=venue_runs.values,
                     color_continuous_scale='Blues')
    fig3.update_xaxes(tickangle=45)
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # with col4:
        # Home team advantage
    venue_city_map = matches_df.groupby('Venue')['City'].first()
        # Simplified home team calculation (you might need to adjust based on actual team-city mapping)
    teams_cities = {
            'Mumbai Indians': 'Mumbai',
            'Chennai Super Kings': 'Chennai',
            'Royal Challengers Bangalore': 'Bangalore',
            'Kolkata Knight Riders': 'Kolkata',
            'Delhi Capitals': 'Delhi'
        }
        
    home_wins = []
    for team, city in teams_cities.items():
            home_matches = matches_df[matches_df['City'] == city]
            home_team_matches = home_matches[(home_matches['Team1'] == team) | (home_matches['Team2'] == team)]
            home_team_wins = home_team_matches[home_team_matches['WinningTeam'] == team]
            if len(home_team_matches) > 0:
                win_pct = len(home_team_wins) / len(home_team_matches) * 100
                home_wins.append({'Team': team, 'Home Win %': win_pct})
        
    if home_wins:
            home_df = pd.DataFrame(home_wins)
            fig4 = px.bar(home_df, x='Team', y='Home Win %',
                         title="Home Team Advantage",
                         color='Home Win %',
                         color_continuous_scale='Greens')
            fig4.update_xaxes(tickangle=45)
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
    
    # Venue Win Pattern Analysis
    st.subheader("Venue Characteristics")
    # col5, col6 = st.columns(2)
    
    # with col5:
        # Batting vs Bowling friendly venues
    venue_first_innings = matches_df[matches_df['TossDecision'] == 'bat']['Venue'].value_counts()
    venue_bat_wins = matches_df[(matches_df['TossDecision'] == 'bat') & 
                                   (matches_df['TossWinner'] == matches_df['WinningTeam'])]['Venue'].value_counts()
        
    batting_friendly = (venue_bat_wins / venue_first_innings * 100).sort_values(ascending=False).head(10)
        
    fig5 = px.bar(x=batting_friendly.index, y=batting_friendly.values,
                     title="Batting Friendly Venues (Win % when batting first)",
                     labels={'x': 'Venues', 'y': 'Win Percentage'},
                     color=batting_friendly.values,
                     color_continuous_scale='Oranges')
    fig5.update_xaxes(tickangle=45)
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)


def season_trends_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">📊 Season-wise Trends</h2>', unsafe_allow_html=True)
    
    # col1, col2 = st.columns(2)
    
    # with col1:
        # Matches per season
    # Normalize Season column
    matches_df['Season'] = matches_df['Season'].replace({'2020/21': '2020', '2007/08': '2008', '2009/10': '2010'})

    def normalize_season(season):
        if '/' in season:
            return int('20' + season.split('/')[1])  # Use ending year
        else:
            return int(season)
    matches_df['Season'] = matches_df['Season'].apply(normalize_season)
    season_matches = matches_df['Season'].value_counts().sort_index()

    print(matches_df['Season'].value_counts().sort_index())

    fig1 = px.bar(x=season_matches.index, y=season_matches.values,
                     title="Number of Matches per Season",
                     labels={'x': 'Season', 'y': 'Number of Matches'},
                     color=season_matches.values,
                     color_continuous_scale='viridis')
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)
    
        # Check all unique seasons
    print("Available seasons:", sorted(matches_df['Season'].unique()))

    # Check for any null values
    print("Null seasons:", matches_df['Season'].isnull().sum())

    # Look at the actual counts
    print("Season counts:")
    print(matches_df['Season'].value_counts().sort_index())
    # with col2:
        # Average runs per season
    season_runs = balls_df.groupby(balls_df['ID'].map(lambda x: 2008 + (x % 14)))['total_run'].mean()
    fig2 = px.line(x=season_runs.index, y=season_runs.values,
                      title="Average Runs per Ball by Season",
                      labels={'x': 'Season', 'y': 'Average Runs per Ball'},
                      markers=True)
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    # col3, col4 = st.columns(2)
    
    # with col3:
        # Toss decision trends
    season_toss = matches_df.groupby(['Season', 'TossDecision']).size().unstack(fill_value=0)
    season_toss_pct = season_toss.div(season_toss.sum(axis=1), axis=0) * 100
        
    fig3 = px.bar(season_toss_pct, 
                     title="Toss Decision Trends by Season (%)",
                     labels={'index': 'Season', 'value': 'Percentage'},
                     barmode='stack')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
        # with col4:
            # Boundary type selection on top of the plot
    boundary_option = st.selectbox(
            "Select Boundary Type", 
            options=["Fours", "Sixes", "Both"], 
            index=2  # Default to "Both"
        )

        # Map selection to batsman_run values
    if boundary_option == "Fours":
            selected_runs = [4]
    elif boundary_option == "Sixes":
            selected_runs = [6]
    else:
            selected_runs = [4, 6]

        # Filter and group by season
    season_boundaries = balls_df[balls_df['batsman_run'].isin(selected_runs)].groupby(
            balls_df['ID'].map(lambda x: 2008 + (x % 14))
        )['batsman_run'].count()

        # Plot
    fig4 = px.line(
            x=season_boundaries.index,
            y=season_boundaries.values,
            title=f"Total {boundary_option} per Season",
            labels={'x': 'Season', 'y': 'Number of Boundaries'},
            markers=True
        )
    fig4.update_layout(height=400)

# Show plot
    st.plotly_chart(fig4, use_container_width=True)

    
    # Season Championship Analysis
    st.subheader("Championship Analysis by Season")
    # col5, col6 = st.columns(2)
    
    # with col5:
        # Winners by season
                # Get season winners data
    matches_df = matches_df.sort_values(by=["Season", "Date"])
    final_matches = matches_df.groupby("Season").tail(1)
    season_winners = final_matches["WinningTeam"].value_counts()


        # Prepare ECharts data format
    winner_data = [{"value": int(count), "name": str(team)} for team, count in season_winners.items()]

        # ECharts configuration
    option = {
            "title": {
                "text": "IPL Championships by Team",
                "left": "center",
                "textStyle": {
                    "fontSize": 16,
                    "fontWeight": "bold",
                    "color": "#333"
                }
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{b}: {c} championships ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "right": 10,
                "top": "center",
                "textStyle": {
                    "fontSize": 12
                }
            },
            "series": [
                {
                    "name": "Championships",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["40%", "50%"],
                    "data": winner_data,
                    "itemStyle": {
                        "borderRadius": 8,
                        "borderColor": "#fff",
                        "borderWidth": 2
                    },
                    "label": {
                        "show": True,
                        "formatter": "{d}%",
                        "fontSize": 12,
                        "color": "#333"
                    },
                    "labelLine": {
                        "show": True,
                        "length": 10,
                        "length2": 15
                    },
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        },
                        "label": {
                            "show": True,
                            "fontWeight": "bold"
                        }
                    }
                }
            ],
            "color": [
                "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
                "#FF9F40", "#8AC24A", "#EA5545", "#F46A9B", "#EF9B20"
            ]
        }

        # Display the chart
    st_echarts(
            options=option,
            height="500px",
            key="ipl_championships_pie"
        )
    # with col6:
        # Most successful teams over years
    yearly_performance = matches_df.groupby(['Season', 'WinningTeam']).size().unstack(fill_value=0)
    cumulative_wins = yearly_performance.cumsum()
        
    fig6 = px.line(cumulative_wins.T, 
                      title="Cumulative Wins Over Seasons",
                      labels={'index': 'Season', 'value': 'Cumulative Wins'})
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)
    
    # Season Statistics Table
    # Merge balls_df and matches_df on the match ID
    merged_df = pd.merge(balls_df, matches_df[['ID', 'Season']], left_on='ID', right_on='ID', how='left')

    # Season Statistics Table
    st.subheader("Season-wise Statistics Summary")

    season_stats = []
    for season in sorted(matches_df['Season'].dropna().unique()):
        season_data = matches_df[matches_df['Season'] == season]
        season_balls = merged_df[merged_df['Season'] == season]
        
        total_matches = len(season_data)
        total_runs = season_balls['total_run'].sum()
        total_boundaries = len(season_balls[season_balls['batsman_run'].isin([4, 6])])
        total_wickets = len(season_balls[season_balls['isWicketDelivery'] == 1])
        
        season_stats.append({
            'Season': season,
            'Matches': total_matches,
            'Total Runs': total_runs,
            'Boundaries': total_boundaries,
            'Wickets': total_wickets,
            'Avg Runs/Match': round(total_runs / total_matches if total_matches > 0 else 0, 1)
        })

    # Convert to DataFrame and show
    season_stats_df = pd.DataFrame(season_stats)
    st.dataframe(season_stats_df, use_container_width=True)

    

def statistical_overview_tab(matches_df, balls_df):
    st.markdown('<h2 class="tab-header">🔢 Statistical Overview</h2>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_matches = len(matches_df)
    total_runs = balls_df['total_run'].sum()
    total_boundaries = len(balls_df[balls_df['batsman_run'].isin([4, 6])])
    total_wickets = len(balls_df[balls_df['isWicketDelivery'] == 1])
    
    with col1:
        st.metric("Total Matches", f"{total_matches:,}")
    with col2:
        st.metric("Total Runs", f"{total_runs:,}")
    with col3:
        st.metric("Total Boundaries", f"{total_boundaries:,}")
    with col4:
        st.metric("Total Wickets", f"{total_wickets:,}")
    
    st.markdown("---")
    
    
    dismissal_data = balls_df[balls_df['isWicketDelivery'] == 1]
    if len(dismissal_data) > 0:
            dismissal_overs = dismissal_data.groupby('overs').size()
            fig2 = px.line(x=dismissal_overs.index, y=dismissal_overs.values,
                          title="Wickets by Over Number",
                          labels={'x': 'Over', 'y': 'Number of Wickets'},
                          markers=True)
    else:
            # Sample data for demonstration
            overs = list(range(0, 20))
            wickets = np.random.poisson(2, 20)
            fig2 = px.line(x=overs, y=wickets,
                          title="Wickets by Over Number (Sample)",
                          labels={'x': 'Over', 'y': 'Number of Wickets'},
                          markers=True)
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    # col7, col8 = st.columns(2)
    
    # with col7:
        # Powerplay Analysis
    powerplay_balls = balls_df[balls_df['overs'] < 6]
    powerplay_runs = powerplay_balls['total_run'].sum()
    powerplay_wickets = len(powerplay_balls[powerplay_balls['isWicketDelivery'] == 1])
    powerplay_balls_count = len(powerplay_balls)
        
    middle_overs_balls = balls_df[(balls_df['overs'] >= 6) & (balls_df['overs'] < 15)]
    middle_runs = middle_overs_balls['total_run'].sum()
    middle_wickets = len(middle_overs_balls[middle_overs_balls['isWicketDelivery'] == 1])
    middle_balls_count = len(middle_overs_balls)
        
    death_overs_balls = balls_df[balls_df['overs'] >= 15]
    death_runs = death_overs_balls['total_run'].sum()
    death_wickets = len(death_overs_balls[death_overs_balls['isWicketDelivery'] == 1])
    death_balls_count = len(death_overs_balls)
        
    phases_data = {
            'Phase': ['Powerplay (1-6)', 'Middle (7-15)', 'Death (16-20)'],
            'Runs': [powerplay_runs, middle_runs, death_runs],
            'Wickets': [powerplay_wickets, middle_wickets, death_wickets],
            'Run Rate': [
                round(powerplay_runs / powerplay_balls_count * 6, 2) if powerplay_balls_count > 0 else 0,
                round(middle_runs / middle_balls_count * 6, 2) if middle_balls_count > 0 else 0,
                round(death_runs / death_balls_count * 6, 2) if death_balls_count > 0 else 0
            ]
        }
        
    phases_df = pd.DataFrame(phases_data)
    fig3 = px.bar(phases_df, x='Phase', y='Run Rate',
                     title="Run Rate by Match Phase",
                     color='Run Rate',
                     color_continuous_scale='Reds')
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # with col8:
        # Extras Analysis
    

    # Get extras data
    extras_data = balls_df[balls_df['extras_run'] > 0]

    if len(extras_data) > 0:
        extras_dist = extras_data['extras_run'].value_counts().sort_index()
        chart_data = [{"value": int(count), "name": f"{str(extra_type)} Extras"} 
                    for extra_type, count in extras_dist.items()]
        chart_title = "Distribution of Extras"
    else:
        # Sample data
        chart_data = [
            {"value": 60, "name": "1 Extra"},
            {"value": 30, "name": "2 Extras"},
            {"value": 10, "name": "4 Extras"}
        ]
        chart_title = "Distribution of Extras (Sample)"

    # ECharts configuration
    option = {
        "title": {
            "text": chart_title,
            "left": "center",
            "textStyle": {
                "fontSize": 16,
                "fontWeight": "bold"
            }
        },
        "tooltip": {
            "trigger": "item",
            "formatter": "{b}: {c} occurrences ({d}%)"
        },
        "series": [
            {
                "name": "Extras Distribution",
                "type": "pie",
                "radius": ["40%", "70%"],
                "data": chart_data,
                "itemStyle": {
                    "borderRadius": 5,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {
                    "show": True,
                    "formatter": "{b}\n{d}%",
                    "fontSize": 12
                },
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    },
                    "label": {
                        "show": True,
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {
                    "show": True
                }
            }
        ],
        "color": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
    }

    # Display the chart
    st_echarts(
        options=option,
        height="400px",
        key="extras_distribution_chart"
    )
    # Advanced Statistics
    st.subheader("Advanced Match Statistics")
    
    # col9, col10 = st.columns(2)
    
    # with col9:
        # Highest Individual Scores
    individual_scores = balls_df.groupby(['ID', 'innings', 'batter'])['batsman_run'].sum().reset_index()
    top_scores = individual_scores.nlargest(15, 'batsman_run')
        
    fig5 = px.bar(top_scores, x='batter', y='batsman_run',
                     title="Top 15 Individual Scores",
                     labels={'batter': 'Batsman', 'batsman_run': 'Runs'},
                     color='batsman_run',
                     color_continuous_scale='viridis')
    fig5.update_xaxes(tickangle=45)
    fig5.update_layout(height=400)
    st.plotly_chart(fig5, use_container_width=True)
    
    # with col10:
        # Best Bowling Figures
    bowling_figures = balls_df.groupby(['ID', 'innings', 'bowler']).agg({
            'isWicketDelivery': 'sum',
            'total_run': 'sum'
        }).reset_index()
    bowling_figures.columns = ['ID', 'innings', 'bowler', 'wickets', 'runs']
    best_bowling = bowling_figures.nlargest(15, 'wickets').nsmallest(15, 'runs')
        
    fig6 = px.scatter(best_bowling, x='runs', y='wickets', hover_data=['bowler'],
                         title="Best Bowling Figures (Wickets vs Runs)",
                         labels={'runs': 'Runs Conceded', 'wickets': 'Wickets Taken'},
                         color='wickets',
                         size='wickets',
                         color_continuous_scale='plasma')
    fig6.update_layout(height=400)
    st.plotly_chart(fig6, use_container_width=True)
    
    # Summary Statistics Table
    st.subheader("Quick Facts & Records")
    
    # Calculate some interesting statistics
    highest_team_total = balls_df.groupby(['ID', 'innings'])['total_run'].sum().max()
    most_boundaries_match = balls_df[balls_df['batsman_run'].isin([4, 6])].groupby('ID').size().max()
    highest_individual = individual_scores['batsman_run'].max()
    most_wickets_bowler = bowling_figures['wickets'].max()
    
    facts_data = {
        'Statistic': [
            'Highest Team Total',
            'Most Boundaries in a Match',
            'Highest Individual Score',
            'Best Bowling Figures (Wickets)',
            'Average Runs per Match',
            'Average Boundaries per Match',
            'Total Dot Balls',
            'Total Balls Bowled'
        ],
        'Value': [
            f"{highest_team_total}",
            f"{most_boundaries_match}",
            f"{highest_individual}",
            f"{most_wickets_bowler}",
            f"{round(total_runs / total_matches, 1)}",
            f"{round(total_boundaries / total_matches, 1)}",
            f"{len(balls_df[balls_df['total_run'] == 0]):,}",
            f"{len(balls_df):,}"
        ]
    }
    
    facts_df = pd.DataFrame(facts_data)
    st.dataframe(facts_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()