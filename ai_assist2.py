#!/usr/bin/env python
"""
US COVID-19 Data Fetcher
------------------------
This script fetches US-specific COVID-19 data from the Johns Hopkins CSSE GitHub repository
using direct URLs to the raw CSV files in the csse_covid_19_daily_reports_us directory.
"""

import os
import logging
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("us_covid_fetcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("us_covid_fetcher")

# Constants
# Note: We're now using the US-specific directory
GITHUB_RAW_URL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/"
DATA_DIR = Path("us_covid_data")
GRAPH_DIR = Path("us_covid_graphs")


class USCovidFetcher:
    """Class for fetching US-specific COVID-19 data directly from GitHub raw URLs"""

    def __init__(
        self,
        start_date: str = "01-01-2021",  # Default to January 2021
        end_date: str = "06-30-2022",    # Default to June 2022
        data_dir: Path = DATA_DIR,
        graph_dir: Path = GRAPH_DIR,
        request_timeout: int = 10
    ):
        """
        Initialize the US COVID data fetcher.

        Args:
            start_date: Start date in format 'MM-DD-YYYY' (defaults to January 1, 2021)
            end_date: End date in format 'MM-DD-YYYY' (defaults to June 30, 2022)
            data_dir: Directory to store raw and processed data
            graph_dir: Directory to store generated graphs
            request_timeout: Timeout for HTTP requests in seconds
        """
        self.request_timeout = request_timeout

        # Setup directories
        self.data_dir = data_dir
        self.graph_dir = graph_dir
        self.data_dir.mkdir(exist_ok=True)
        self.graph_dir.mkdir(exist_ok=True)

        # Setup dates
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)

        self.start_date = self._parse_date(start_date)
        self.end_date = self._parse_date(end_date)

        logger.info(f"Date range: {self.start_date.strftime('%m-%d-%Y')} to {self.end_date.strftime('%m-%d-%Y')}")

        # Initialize data storage
        self.data = pd.DataFrame()

    def _parse_date(self, date_str: str) -> date:
        """Parse date string in format MM-DD-YYYY"""
        try:
            return datetime.strptime(date_str, '%m-%d-%Y').date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected format: MM-DD-YYYY")

    def _get_date_range(self) -> List[str]:
        """Get list of dates between start_date and end_date in format MM-DD-YYYY"""
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        return [d.strftime('%m-%d-%Y') for d in date_range]

    def fetch_csv(self, date_str: str) -> Optional[str]:
        """
        Fetch CSV data for a specific date directly using the raw GitHub URL.

        Args:
            date_str: Date in format MM-DD-YYYY

        Returns:
            Raw CSV content as string, or None if fetching failed
        """
        logger.info(f"Fetching US data for {date_str}")

        # Check if we already have the file
        csv_path = self.data_dir / f"us_covid_{date_str.replace('-', '_')}.csv"
        if csv_path.exists():
            logger.info(f"Data for {date_str} already exists, reading from file")
            with open(csv_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Build the direct URL to the raw CSV file
        url = f"{GITHUB_RAW_URL}{date_str}.csv"
        logger.info(f"Fetching from URL: {url}")

        try:
            # Use requests library to get the content directly
            response = requests.get(url, timeout=self.request_timeout)

            if response.status_code == 200:
                # Save the content to file
                with open(csv_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                logger.info(f"Successfully fetched data for {date_str}")
                return response.text
            else:
                logger.warning(f"Failed to fetch data for {date_str}: HTTP status {response.status_code}")
                # Save a marker file to indicate we tried but failed
                with open(csv_path.with_suffix('.404'), 'w') as f:
                    f.write(f"Failed to fetch on {datetime.now()}, status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {date_str}: {e}")
            return None

    def process_csv_data(self, raw_content: str, date_str: str) -> pd.DataFrame:
        """
        Process raw CSV content into a DataFrame.

        Args:
            raw_content: Raw CSV content as string
            date_str: Date in format MM-DD-YYYY

        Returns:
            Processed DataFrame
        """
        try:
            # Parse CSV content
            df = pd.read_csv(pd.StringIO(raw_content))

            # Check that this is valid data with expected columns
            required_cols = ['Province_State', 'Confirmed', 'Deaths']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"CSV for {date_str} missing required columns. Found: {df.columns.tolist()}")
                return pd.DataFrame()

            # Handle missing values
            for col in df.columns:
                if df[col].isnull().any():
                    if pd.api.types.is_numeric_dtype(df[col]):
                        df[col] = df[col].fillna(0)
                    else:
                        df[col] = df[col].fillna('')

            # Handle column name variations
            column_name_fixes = {
                'Case-Fatality_Ratio': 'Case_Fatality_Ratio',
                'Incident_Rate': 'Incidence_Rate',
                'Last Update': 'Last_Update'
            }

            df = df.rename(columns=column_name_fixes)

            # Convert date columns
            date_columns = ['Last_Update']
            for col in date_columns:
                if col in df.columns:
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        logger.warning(f"Failed to convert {col} to datetime")

            # Add the date as a column for reference
            df['Report_Date'] = pd.to_datetime(date_str, format='%m-%d-%Y')

            return df

        except Exception as e:
            logger.error(f"Error processing CSV data for {date_str}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return pd.DataFrame()

    def fetch_all_dates(self):
        """Fetch data for all dates in the range"""
        date_range = self._get_date_range()
        if not date_range:
            logger.warning("No dates to fetch")
            return

        logger.info(f"Preparing to fetch {len(date_range)} dates from {date_range[0]} to {date_range[-1]}")

        all_dfs = []
        failed_dates = []

        for date_str in date_range:
            try:
                # Add a small delay between requests to be nice to the server
                if date_str != date_range[0]:
                    time.sleep(0.5)

                raw_content = self.fetch_csv(date_str)
                if raw_content:
                    df = self.process_csv_data(raw_content, date_str)
                    if not df.empty:
                        all_dfs.append(df)
                        logger.info(f"Successfully processed data for {date_str}")
                    else:
                        failed_dates.append(date_str)
                else:
                    failed_dates.append(date_str)

            except Exception as e:
                logger.error(f"Error processing date {date_str}: {e}")
                failed_dates.append(date_str)
                continue

        # Combine all DataFrames
        if all_dfs:
            self.data = pd.concat(all_dfs, ignore_index=True)
            # Save combined data
            combined_path = self.data_dir / f"us_covid_combined_{self.start_date.strftime('%m_%d_%Y')}_to_{self.end_date.strftime('%m_%d_%Y')}.csv"
            self.data.to_csv(combined_path, index=False)
            logger.info(f"Saved combined data to {combined_path}")

            # Log summary of the fetch
            success_count = len(all_dfs)
            failed_count = len(failed_dates)
            total_count = len(date_range)
            logger.info(f"Fetch summary: {success_count}/{total_count} successful ({success_count/total_count*100:.1f}%)")
            if failed_dates:
                logger.warning(f"Failed dates: {', '.join(failed_dates[:10])}{'...' if len(failed_dates) > 10 else ''}")
        else:
            logger.warning("No data was fetched")

    def generate_visualizations(self, states: List[str] = None):
        """
        Generate visualizations for the specified states.

        Args:
            states: List of US states to visualize, or None for all states in the data
        """
        if self.data.empty:
            logger.warning("No data to visualize")
            return

        # Filter to only rows with confirmed cases
        data = self.data[self.data['Confirmed'] > 0].copy()

        # If no states specified, get all unique states
        if not states:
            try:
                states = data['Province_State'].unique().tolist()
            except KeyError:
                logger.error("Province_State column not found in data")
                return

        for state in states:
            try:
                # Filter data for this state
                state_data = data[data['Province_State'] == state].copy()

                if state_data.empty:
                    logger.warning(f"No data for state: {state}")
                    continue

                # Group by report date for time series analysis
                state_time_series = state_data.groupby('Report_Date').agg({
                    'Confirmed': 'max',  # Use max since we want the cumulative count
                    'Deaths': 'max',
                    'Incident_Rate': 'max' if 'Incident_Rate' in state_data.columns else lambda x: np.nan,
                    'Case_Fatality_Ratio': 'max' if 'Case_Fatality_Ratio' in state_data.columns else lambda x: np.nan
                }).reset_index()

                # Sort by date
                state_time_series = state_time_series.sort_values('Report_Date')

                # Calculate daily new cases and deaths
                state_time_series['New_Cases'] = state_time_series['Confirmed'].diff().fillna(0)
                state_time_series['New_Deaths'] = state_time_series['Deaths'].diff().fillna(0)

                # Replace negative values with 0 (data corrections)
                state_time_series['New_Cases'] = state_time_series['New_Cases'].clip(lower=0)
                state_time_series['New_Deaths'] = state_time_series['New_Deaths'].clip(lower=0)

                # Calculate 7-day moving averages
                state_time_series['New_Cases_7day_Avg'] = state_time_series['New_Cases'].rolling(7).mean()
                state_time_series['New_Deaths_7day_Avg'] = state_time_series['New_Deaths'].rolling(7).mean()

                # Create a multi-panel figure
                fig, axes = plt.subplots(2, 2, figsize=(20, 16))

                # Plot 1: Cumulative cases and deaths
                ax1 = axes[0, 0]
                ax1_twin = ax1.twinx()

                state_time_series.plot(x='Report_Date', y='Confirmed', ax=ax1, color='blue', legend=False)
                state_time_series.plot(x='Report_Date', y='Deaths', ax=ax1_twin, color='red', legend=False)

                ax1.set_title(f"{state}: Cumulative COVID-19 Cases and Deaths", fontsize=14)
                ax1.set_ylabel('Confirmed Cases', color='blue', fontsize=12)
                ax1_twin.set_ylabel('Deaths', color='red', fontsize=12)
                ax1.grid(True, alpha=0.3)

                # Add legend
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax1_twin.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, ['Confirmed Cases', 'Deaths'], loc='upper left')

                # Plot 2: Daily new cases and 7-day average
                ax2 = axes[0, 1]

                ax2.bar(state_time_series['Report_Date'], state_time_series['New_Cases'],
                       alpha=0.3, color='blue', label='Daily New Cases')
                ax2.plot(state_time_series['Report_Date'], state_time_series['New_Cases_7day_Avg'],
                        color='blue', linewidth=2, label='7-day Moving Average')

                ax2.set_title(f"{state}: Daily New COVID-19 Cases", fontsize=14)
                ax2.set_ylabel('New Cases', fontsize=12)
                ax2.legend(loc='upper left')
                ax2.grid(True, alpha=0.3)

                # Plot 3: Daily new deaths and 7-day average
                ax3 = axes[1, 0]

                ax3.bar(state_time_series['Report_Date'], state_time_series['New_Deaths'],
                       alpha=0.3, color='red', label='Daily New Deaths')
                ax3.plot(state_time_series['Report_Date'], state_time_series['New_Deaths_7day_Avg'],
                        color='red', linewidth=2, label='7-day Moving Average')

                ax3.set_title(f"{state}: Daily New COVID-19 Deaths", fontsize=14)
                ax3.set_ylabel('New Deaths', fontsize=12)
                ax3.legend(loc='upper left')
                ax3.grid(True, alpha=0.3)

                # Plot 4: Case fatality ratio
                ax4 = axes[1, 1]

                if 'Case_Fatality_Ratio' in state_time_series.columns:
                    state_time_series.plot(x='Report_Date', y='Case_Fatality_Ratio', ax=ax4,
                                          color='purple', legend=False)
                    ax4.set_title(f"{state}: COVID-19 Case Fatality Ratio (%)", fontsize=14)
                    ax4.set_ylabel('Case Fatality Ratio (%)', fontsize=12)
                    ax4.grid(True, alpha=0.3)
                else:
                    ax4.text(0.5, 0.5, 'Case Fatality Ratio data not available',
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax4.transAxes, fontsize=12)
                    ax4.set_title(f"{state}: COVID-19 Case Fatality Ratio", fontsize=14)

                # Improve layout
                plt.tight_layout()
                plt.subplots_adjust(top=0.9)
                fig.suptitle(f"COVID-19 Analysis for {state}\n{self.start_date.strftime('%B %d, %Y')} to {self.end_date.strftime('%B %d, %Y')}",
                            fontsize=16)

                # Save the figure
                plot_path = self.graph_dir / f"{state.replace(' ', '_')}_covid_analysis.png"
                plt.savefig(plot_path, dpi=300)
                plt.close(fig)
                logger.info(f"Saved analysis plot to {plot_path}")

                # Create an additional time series comparison with other selected states
                # We'll do this only for the main states we're analyzing
                if states and len(states) > 1:
                    self.create_state_comparison(state, states)

            except Exception as e:
                logger.error(f"Error generating visualization for {state}: {e}")
                import traceback
                logger.error(traceback.format_exc())

    def create_state_comparison(self, focal_state: str, comparison_states: List[str]):
        """
        Create a comparison visualization between the focal state and other states.

        Args:
            focal_state: The main state to highlight
            comparison_states: List of states to compare against
        """
        try:
            # Get data for all specified states
            states_to_compare = [s for s in comparison_states if s != focal_state][:4]  # Limit to 4 other states
            all_comparison_states = [focal_state] + states_to_compare

            # Prepare a figure with multiple plots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))

            # 1. Compare confirmed cases per 100k population
            for state in all_comparison_states:
                state_data = self.data[self.data['Province_State'] == state].copy()
                if state_data.empty:
                    continue

                # Group by date
                grouped = state_data.groupby('Report_Date').agg({
                    'Incident_Rate': 'max' if 'Incident_Rate' in state_data.columns else lambda x: np.nan
                }).reset_index()

                # Plot incident rate if available
                if 'Incident_Rate' in grouped.columns and not grouped['Incident_Rate'].isnull().all():
                    grouped = grouped.sort_values('Report_Date')
                    linestyle = '-' if state == focal_state else '--'
                    linewidth = 2.5 if state == focal_state else 1.5
                    ax1.plot(grouped['Report_Date'], grouped['Incident_Rate'],
                            label=state, linestyle=linestyle, linewidth=linewidth)

            ax1.set_title(f"COVID-19 Cases per 100,000 Population: {focal_state} vs. Other States", fontsize=14)
            ax1.set_ylabel('Cases per 100k Population', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # 2. Compare case fatality ratios
            for state in all_comparison_states:
                state_data = self.data[self.data['Province_State'] == state].copy()
                if state_data.empty:
                    continue

                # Group by date
                grouped = state_data.groupby('Report_Date').agg({
                    'Case_Fatality_Ratio': 'max' if 'Case_Fatality_Ratio' in state_data.columns else lambda x: np.nan
                }).reset_index()

                # Plot case fatality ratio if available
                if 'Case_Fatality_Ratio' in grouped.columns and not grouped['Case_Fatality_Ratio'].isnull().all():
                    grouped = grouped.sort_values('Report_Date')
                    linestyle = '-' if state == focal_state else '--'
                    linewidth = 2.5 if state == focal_state else 1.5
                    ax2.plot(grouped['Report_Date'], grouped['Case_Fatality_Ratio'],
                            label=state, linestyle=linestyle, linewidth=linewidth)

            ax2.set_title(f"COVID-19 Case Fatality Ratio: {focal_state} vs. Other States", fontsize=14)
            ax2.set_ylabel('Case Fatality Ratio (%)', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.legend()

            # Improve layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            fig.suptitle(f"COVID-19 Comparison: {focal_state} vs. Other States\n{self.start_date.strftime('%B %d, %Y')} to {self.end_date.strftime('%B %d, %Y')}",
                        fontsize=16)

            # Save the figure
            plot_path = self.graph_dir / f"{focal_state.replace(' ', '_')}_comparison.png"
            plt.savefig(plot_path, dpi=300)
            plt.close(fig)
            logger.info(f"Saved comparison plot to {plot_path}")

        except Exception as e:
            logger.error(f"Error creating state comparison for {focal_state}: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def generate_national_summary(self):
        """Generate a national summary of COVID-19 statistics"""
        if self.data.empty:
            logger.warning("No data to generate national summary")
            return

        try:
            # Create a national time series by aggregating all states
            national_data = self.data.groupby('Report_Date').agg({
                'Confirmed': 'sum',
                'Deaths': 'sum',
                'Incident_Rate': 'mean' if 'Incident_Rate' in self.data.columns else lambda x: np.nan,
                'Case_Fatality_Ratio': 'mean' if 'Case_Fatality_Ratio' in self.data.columns else lambda x: np.nan
            }).reset_index()

            # Sort by date
            national_data = national_data.sort_values('Report_Date')

            # Calculate daily new cases and deaths
            national_data['New_Cases'] = national_data['Confirmed'].diff().fillna(0)
            national_data['New_Deaths'] = national_data['Deaths'].diff().fillna(0)

            # Replace negative values with 0 (data corrections)
            national_data['New_Cases'] = national_data['New_Cases'].clip(lower=0)
            national_data['New_Deaths'] = national_data['New_Deaths'].clip(lower=0)

            # Calculate 7-day moving averages
            national_data['New_Cases_7day_Avg'] = national_data['New_Cases'].rolling(7).mean()
            national_data['New_Deaths_7day_Avg'] = national_data['New_Deaths'].rolling(7).mean()

            # Create a summary visualization
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))

            # Plot 1: Cumulative cases and deaths
            ax1 = axes[0, 0]
            ax1_twin = ax1.twinx()

            national_data.plot(x='Report_Date', y='Confirmed', ax=ax1, color='blue', legend=False)
            national_data.plot(x='Report_Date', y='Deaths', ax=ax1_twin, color='red', legend=False)

            ax1.set_title("US National: Cumulative COVID-19 Cases and Deaths", fontsize=14)
            ax1.set_ylabel('Confirmed Cases', color='blue', fontsize=12)
            ax1_twin.set_ylabel('Deaths', color='red', fontsize=12)
            ax1.grid(True, alpha=0.3)

            # Add legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, ['Confirmed Cases', 'Deaths'], loc='upper left')

            # Format y-axis with millions/thousands
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000000:.1f}M"))
            ax1_twin.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000:.0f}K"))

            # Plot 2: Daily new cases and 7-day average
            ax2 = axes[0, 1]

            ax2.bar(national_data['Report_Date'], national_data['New_Cases'],
                   alpha=0.3, color='blue', label='Daily New Cases')
            ax2.plot(national_data['Report_Date'], national_data['New_Cases_7day_Avg'],
                    color='blue', linewidth=2, label='7-day Moving Average')

            ax2.set_title("US National: Daily New COVID-19 Cases", fontsize=14)
            ax2.set_ylabel('New Cases', fontsize=12)
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3)

            # Format y-axis with thousands
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000:.0f}K"))

            # Plot 3: Daily new deaths and 7-day average
            ax3 = axes[1, 0]

            ax3.bar(national_data['Report_Date'], national_data['New_Deaths'],
                   alpha=0.3, color='red', label='Daily New Deaths')
            ax3.plot(national_data['Report_Date'], national_data['New_Deaths_7day_Avg'],
                    color='red', linewidth=2, label='7-day Moving Average')

            ax3.set_title("US National: Daily New COVID-19 Deaths", fontsize=14)
            ax3.set_ylabel('New Deaths', fontsize=12)
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3)

            # Plot 4: Case fatality ratio
            ax4 = axes[1, 1]

            if 'Case_Fatality_Ratio' in national_data.columns:
                national_data.plot(x='Report_Date', y='Case_Fatality_Ratio', ax=ax4,
                                  color='purple', legend=False)
                ax4.set_title("US National: COVID-19 Case Fatality Ratio (%)", fontsize=14)
                ax4.set_ylabel('Case Fatality Ratio (%)', fontsize=12)
                ax4.grid(True, alpha=0.3)
            else:
                ax4.text(0.5, 0.5, 'Case Fatality Ratio data not available',
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax4.transAxes, fontsize=12)
                ax4.set_title("US National: COVID-19 Case Fatality Ratio", fontsize=14)

            # Improve layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            fig.suptitle(f"US National COVID-19 Analysis\n{self.start_date.strftime('%B %d, %Y')} to {self.end_date.strftime('%B %d, %Y')}",
                        fontsize=16)

            # Save the figure
            plot_path = self.graph_dir / "US_National_covid_analysis.png"
            plt.savefig(plot_path, dpi=300)
            plt.close(fig)
            logger.info(f"Saved national analysis plot to {plot_path}")

            # Create top states comparison
            self.create_top_states_comparison(national_data)

        except Exception as e:
            logger.error(f"Error generating national summary: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def create_top_states_comparison(self, national_data):
        """Create a comparison of top states by cases, deaths, and fatality ratio"""
        try:
            # Get the latest data for each state
            latest_date = self.data['Report_Date'].max()
            latest_data = self.data[self.data['Report_Date'] == latest_date].copy()

            if latest_data.empty:
                logger.warning("No latest data available for top states comparison")
                return

            # Create a figure with three subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 18))

            # 1. Top 10 states by confirmed cases
            top_cases = latest_data.nlargest(10, 'Confirmed')
            colors1 = plt.cm.Blues(np.linspace(0.5, 1.0, len(top_cases)))
            top_cases.sort_values('Confirmed').plot(kind='barh', x='Province_State', y='Confirmed',
                                                  ax=ax1, color=colors1, legend=False)
            ax1.set_title('Top 10 States by COVID-19 Confirmed Cases', fontsize=14)
            ax1.set_xlabel('Confirmed Cases', fontsize=12)
            ax1.grid(True, alpha=0.3, axis='x')

            # Format x-axis with millions
            ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000000:.1f}M"))

            # Add data labels
            for i, v in enumerate(top_cases['Confirmed']):
                ax1.text(v, i, f"{v/1000000:.1f}M", va='center', fontsize=9)

            # 2. Top 10 states by deaths
            top_deaths = latest_data.nlargest(10, 'Deaths')
            colors2 = plt.cm.Reds(np.linspace(0.5, 1.0, len(top_deaths)))
            top_deaths.sort_values('Deaths').plot(kind='barh', x='Province_State', y='Deaths',
                                                ax=ax2, color=colors2, legend=False)
            ax2.set_title('Top 10 States by COVID-19 Deaths', fontsize=14)
            ax2.set_xlabel('Deaths', fontsize=12)
            ax2.grid(True, alpha=0.3, axis='x')

            # Format x-axis with thousands
            ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000:.0f}K"))

            # Add data labels
            for i, v in enumerate(top_deaths['Deaths']):
                ax2.text(v, i, f"{v/1000:.1f}K", va='center', fontsize=9)

            # 3. Top and bottom 5 states by case fatality ratio (excluding outliers)
            if 'Case_Fatality_Ratio' in latest_data.columns:
                # Filter out states with unrealistic CFR (e.g., >10%)
                cfr_data = latest_data[(latest_data['Case_Fatality_Ratio'] > 0) &
                                     (latest_data['Case_Fatality_Ratio'] < 10) &
                                     (latest_data['Confirmed'] > 1000)]  # Exclude small case counts

                # Get top 5 and bottom 5
                top_cfr = cfr_data.nlargest(5, 'Case_Fatality_Ratio')
                bottom_cfr = cfr_data.nsmallest(5, 'Case_Fatality_Ratio')

                # Combine and sort
                combined_cfr = pd.concat([top_cfr, bottom_cfr])
                combined_cfr = combined_cfr.sort_values('Case_Fatality_Ratio')

                # Create a colormap with red for high CFR, blue for low CFR
                colors3 = []
                for i in range(len(combined_cfr)):
                    if i < 5:  # Bottom 5 (blue)
                        colors3.append(plt.cm.Blues(0.7))
                    else:  # Top 5 (red)
                        colors3.append(plt.cm.Reds(0.7))

                combined_cfr.plot(kind='barh', x='Province_State', y='Case_Fatality_Ratio',
                                ax=ax3, color=colors3, legend=False)
                ax3.set_title('States with Highest and Lowest Case Fatality Ratios', fontsize=14)
                ax3.set_xlabel('Case Fatality Ratio (%)', fontsize=12)
                ax3.grid(True, alpha=0.3, axis='x')

                # Add data labels
                for i, v in enumerate(combined_cfr['Case_Fatality_Ratio']):
                    ax3.text(v, i, f"{v:.2f}%", va='center', fontsize=9)
            else:
                ax3.text(0.5, 0.5, 'Case Fatality Ratio data not available',
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax3.transAxes, fontsize=12)
                ax3.set_title('States with Highest and Lowest Case Fatality Ratios', fontsize=14)

            # Improve layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.9)
            fig.suptitle(f"US States COVID-19 Comparison\nAs of {latest_date.strftime('%B %d, %Y')}",
                        fontsize=16)

            # Save the figure
            plot_path = self.graph_dir / "US_States_comparison.png"
            plt.savefig(plot_path, dpi=300)
            plt.close(fig)
            logger.info(f"Saved states comparison plot to {plot_path}")

        except Exception as e:
            logger.error(f"Error creating top states comparison: {e}")
            import traceback
            logger.error(traceback.format_exc())


def main():
    """Main entry point"""
    # Create directories if they don't exist
    data_dir = Path("us_covid_data")
    graph_dir = Path("us_covid_graphs")
    data_dir.mkdir(exist_ok=True)
    graph_dir.mkdir(exist_ok=True)

    # Set the date range from January 2021 to June 2022
    start_date = "01-01-2021"
    end_date = "06-30-2022"

    # Create the fetcher
    fetcher = USCovidFetcher(
        start_date=start_date,
        end_date=end_date,
        data_dir=data_dir,
        graph_dir=graph_dir,
        request_timeout=15  # Increase timeout for slower connections
    )

    try:
        # Fetch the data
        fetcher.fetch_all_dates()

        # Check if we got any data
        if not fetcher.data.empty:
            logger.info(f"Successfully fetched data with {len(fetcher.data)} rows")

            # Generate national summary
            fetcher.generate_national_summary()

            # Generate visualizations for specific states
            fetcher.generate_visualizations(states=[
                "New York",
                "California",
                "Texas",
                "Florida",
                "Washington"
            ])
        else:
            logger.warning("No data was fetched. Check the logs for errors.")

    except Exception as e:
        logger.error(f"Error in main process: {e}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()

