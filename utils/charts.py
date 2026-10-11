import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_candlestick_chart(df):
    # Create a figure with 2 rows (Price on top, Volume on bottom)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=('Price', 'Volume'),
                        row_width=[0.2, 0.7])

    # Candlestick trace
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Price'
    ), row=1, col=1)

    # Volume trace
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Volume'],
        name='Volume',
        marker_color='rgba(128, 128, 128, 0.5)'
    ), row=2, col=1)

    # Update layout for a professional dark/clean look
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    return fig