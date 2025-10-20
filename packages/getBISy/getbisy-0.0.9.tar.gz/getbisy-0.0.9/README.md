# getBISy

A Python package for programmatically fetching and working with Bank for International Settlements (BIS) datasets.

The package currently allows access to the following sets of international financial statistics via the BIS data portal.

- Central Bank policy rates
- Bilateral exchange rates
- Locational banking statistics
- International debt securities
- Global liquidity
- Debt securities

All major parameters are declared in custom enums to ensure error-resistant paramaterisation.

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```
## Usage

The below covers gathering and plotting two datasets gathered from the BIS Data Portal using this package: locational banking statistics (LBS) and Global Liquidity Indicators (GLI)

### Locational Banking Statistics

Import the relevant data functions and enums:

```python
# Test LBS

import getBISy.data as data
import getBISy.enums as enums

# Developing Asia and Pacific, Non-banks, Cross-border Credit, USD
s1 = data.get_locational_banking_data('Q',
                                        enums.LbsMeasure.Stocks,
                                        enums.Position.Claims,
                                        enums.Instrument.LoansAndDeposits,
                                        'USD',
                                        enums.CurrencyType.All,
                                        '5J',
                                        enums.Institution.All,
                                        '5A',
                                        enums.Sector.NonBanks,
                                        enums.Region.DevelopingAsiaAndPacific,
                                        enums.PositionType.CrossBorder)

s1['Description'] = 'Developing Asia and Pacific, Non-banks, Cross-border Credit, USD'

# European Developed Countries, Non-banks, Cross-border Credit, USD
s2 = data.get_locational_banking_data('Q',
                                        enums.LbsMeasure.Stocks,
                                        enums.Position.Claims,
                                        enums.Instrument.LoansAndDeposits,
                                        'USD',
                                        enums.CurrencyType.All,
                                        '5J',
                                        enums.Institution.All,
                                        '5A',
                                        enums.Sector.NonBanks,
                                        enums.Region.EuropeanDevelopedCountries,
                                        enums.PositionType.CrossBorder)

s2['Description'] = 'European Developed Countries, Non-banks, Cross-border Credit, USD'

```


Once you have the data, we can plot it and give it a descriptive title.

```python
from pandas import DataFrame, PeriodIndex, to_numeric
import plotly.express as px
import plotly.graph_objects as go

fig = go.Figure()

for df in [s1, s2]:
    # Convert quarterly periods to timestamps
    df['Date'] = PeriodIndex(df['Date'], freq='Q').to_timestamp()
    df['Value'] = to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    df = df.sort_values(by='Date')

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Value'],
        mode='lines+markers',
        name=df['Description'].iloc[0]
    ))

fig.update_layout(
    title=dict(
        text='Paths of cross-border bank credit between Europe vs. Developing Asia are diverging',
        x=0.5,
        xanchor='center',
        font=dict(size=20)
    ),
    xaxis_title='Date',
    yaxis_title='USD (millions)',
    hovermode='x unified',
    yaxis=dict(autorange=True, tickformat=".0f"),
    width=1000,
    height=600,
    legend=dict(
        title=dict(text='Series'),
        font=dict(size=12),
        orientation='h',
        yanchor='top',
        y=-0.2,  # Move legend below the plot
        xanchor='center',
        x=0.5
    )
)
```
![LBS Example](LBS.png)


### Global Liquidity Indicators

As in the LBS example above, import the relevant functions and enums:

```python 

import getBISy.data as data
import getBISy.enums as enums

s1 = data.get_global_liquidity_data(freq='Q',
                               currency='TO1',
                               borrowing_country=enums.Region.DevelopingAsiaAndPacific,
                               borrowing_sector=enums.Sector.NonFinancialPrivateSector,
                               lending_sector=enums.Sector.Banks,
                               position_type= enums.PositionType.Local,
                               instrument_type=enums.Instrument.Credit,
                               unit_of_measure=enums.UnitOfMeasure.PercentageOfGDP
                               )

s2 = data.get_global_liquidity_data(freq='Q',
                               currency='TO1',
                               borrowing_country=enums.Region.EuroArea,
                               borrowing_sector=enums.Sector.NonFinancialPrivateSector,
                               lending_sector=enums.Sector.Banks,
                               position_type= enums.PositionType.Local,
                               instrument_type=enums.Instrument.Credit,
                               unit_of_measure=enums.UnitOfMeasure.PercentageOfGDP
                               )

```

Given the below plot in the context of the above, we infer that local bank credit to non-financial private sector in Developing Asia is replacing cross-border credit. 

```python
from pandas import PeriodIndex, to_numeric
import plotly.express as px
import plotly.graph_objects as go

fig = go.Figure()

for df in [s1, s2]:
    # Convert quarterly periods to timestamps
    df['Date'] = PeriodIndex(df['Date'], freq='Q').to_timestamp()
    df['Value'] = to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    df = df.sort_values(by='Date')

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Value'],
        mode='lines+markers',
        name=df['Description'].iloc[0]
    ))

fig.update_layout(
    title=dict(
        text='Local bank credit to non-financial private sector in Developing Asia is replacing cross-border credit',
        x=0.5,
        xanchor='center',
        font=dict(size=20)
    ),
    xaxis_title='Date',
    yaxis_title='Percentage of GDP',
    hovermode='x unified',
    yaxis=dict(autorange=True, tickformat=".0f"),
    width=1000,
    height=600,
    legend=dict(
        title=dict(text='Series'),
        font=dict(size=12),
        orientation='h',
        yanchor='top',
        y=-0.2,  # Move legend below the plot
        xanchor='center',
        x=0.5
    )
)
```
![GLI Example](GLI.png)

## Project Structure
```
getBISy/
├── src/
│   ├── __init__.py
│   ├── data.py         # Main data-fetching functions
│   ├── enums.py        # Enum definitions for all API parameters
│   └── fetcher.py      # Fetcher classes for making API requests
├── requirements.txt
```
