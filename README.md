
# BTC Portfolio Tracker

BTC Portfolio Tracker is a web application designed to help users manage and track their Bitcoin investment portfolios. The primary goal of the project is to provide users with a comprehensive tool to monitor their Bitcoin holdings, track transaction history, and analyze portfolio performance over time.

It is one of my first project. My goal was to make this app work. I understand the code can be cleaner and more efficient but I am still learning and working on myself.



## Key Features
- Portfolio Management:

  Users can create and manage multiple portfolios to organize their Bitcoin investments.
- Real-time Price Data:

  Utilizing the CryptoCompare API, the application fetches both historical and current prices of Bitcoin to provide users with up-to-date market information.
- Transaction Tracking:

  Users can easily add transactions to their portfolios by inputting the amount of Bitcoin purchased and the transaction date. The application automatically retrieves price information, simplifying the tracking process.
- Portfolio Statistics:

  The app calculates and displays key portfolio statistics, including Return on Investment (ROI), Net Result, Value Invested, and ROI development over time.

## How It Works
- User Registration:

  Users can create accounts to access the portfolio tracking features.
- Portfolio Creation:

  After logging in, users can create individual portfolios, each representing a distinct investment strategy or goal.
- Transaction Logging:

  Users add transactions to their portfolios by specifying the amount of Bitcoin bought and the transaction date. The application automatically fetches price data and saves the transaction details.
- Portfolio Analysis:

  Users can view detailed statistics for each portfolio, allowing them to assess their investment performance and make informed decisions.
## Why BTC Portfolio Tracker?
- Simplicity and Automation:

  The application streamlines the process of tracking Bitcoin investments by automating price retrieval and transaction logging.
- Comprehensive Insights:

  Users gain a deeper understanding of their portfolio's performance through detailed statistics and historical data.
- User-Friendly Interface:

  The user interface is designed to be intuitive, making it easy for both novice and experienced investors to use the platform effectively.

BTC Portfolio Tracker is the ideal solution for Bitcoin investors seeking a user-friendly and efficient tool to monitor and analyze their investment portfolios.
## Installation

To run the project locally, follow these steps:

#### 1. Clone the repository:


```bash
git clone https://github.com/mvace/btc_tracker
```

#### 2. Navigate to the project directory:

```bash
cd btc_tracker
```

#### 3. Create and Activate a Virtual Environment

```bash
python -m venv venv
```
#### On Windows:
```bash
.\venv\Scripts\activate
```

#### On macOS and Linux:
```bash
source venv/bin/activate
```

#### 4. Install dependencies:

```bash
pip install -r requirements.txt
```

#### 5. Run the Development Server

```bash
python manage.py runserver
```

#### 6. Access the Application
Visit http://localhost:8000 in your web browser to access the BTC Portfolio Tracker.


#### 7. Register, Login
Register new user, login, create new portfolio, add transactions