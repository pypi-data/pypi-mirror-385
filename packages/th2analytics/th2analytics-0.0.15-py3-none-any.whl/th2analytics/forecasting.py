import requests
import plotly.graph_objects as go

class ForecastingAPI:
    def __init__(self, base_url, api_token):
        """
        Initialize the API wrapper with a base URL and API token.
        """
        self.base_url = base_url
        self.api_token = api_token

    def th2forecast_api(self, actuals, fcast_horizon, group_target, target_var, date_var, models_list):
        """
        Generate a forecast by sending a request to the API.
        """
        endpoint = "thaink2/forecasting"
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "actuals": actuals.to_json(orient="records", date_format = "iso"),
            "fcast_horizon": fcast_horizon,
            "group_target": group_target,
            "target_var": target_var,
            "date_var": date_var,
            "models_list": models_list
        }

        # Make the API call
        response = requests.post(url, json=payload, headers=headers)

        # Handle response
        if response.status_code == 200:
            return response.json()  # Return the parsed JSON response
        else:
            response.raise_for_status()  # Raise an exception for HTTP errors


def split_forecasts_by_model(forecast_df, model_dict):
    """
    Splits forecast data by model using a model dictionary.

    Args:
        forecast_df (pd.DataFrame): The DataFrame containing forecast data.
        model_dict (dict): Dictionary mapping model IDs to model names.

    Returns:
        dict: A dictionary where keys are model names and values are DataFrames of forecast data for each model.
    """
    return {
        model_dict[model_id]: forecast_df[forecast_df['.model_id'] == model_id]
        for model_id in model_dict
    }

def create_line_plot(filtered_data, forecasts, title, yaxis_title, zoom_range):
    """
    Creates a line plot for visualizing actuals and forecast data.

    Args:
        filtered_data (pd.DataFrame): Historical data.
        forecasts (dict): Dictionary of forecast data by model.
        title (str): Title of the plot.
        yaxis_title (str): Label for the y-axis.
        zoom_range (list): Range for the x-axis zoom.

    Returns:
        plotly.graph_objects.Figure: The generated line plot.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_data['date'],
        y=filtered_data['value'],
        mode='lines+markers',
        name='Actuals',
        marker=dict(color='blue', size=6),
        line=dict(color='blue', width=2)
    ))
    for model, model_data in forecasts.items():
        fig.add_trace(go.Scatter(
            x=model_data['date'],
            y=model_data['value'],
            mode='lines+markers',
            name=f'{model}',
            marker=dict(size=5),
            line=dict(width=2)
        ))
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        template="plotly_white",
        showlegend=True,
        xaxis=dict(range=zoom_range)
    )
    return fig