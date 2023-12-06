from datetime import datetime
from decimal import Decimal
import cryptocompare
import plotly.graph_objects as go
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PortfolioForm
from .models import DailyClosePrice, Transaction, Portfolio, PortfolioMetrics
from .forms import TransactionForm
import requests

api_key = "71519726c4ebf2d4f41b3687d06386ba7c3a07d41ed4e1db77d2394e6b0fd540"
cryptocompare.cryptocompare._set_api_key_parameter(api_key)


@login_required
def index(request):
    portfolios = Portfolio.objects.filter(user=request.user.id)
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, ("Portfolio Created"))
            return redirect("index")
    else:
        form = PortfolioForm()

    return render(
        request,
        "core/index.html",
        {"portfolios": portfolios, "form": form},
    )


@login_required
def transaction_view(request, pk):
    # Retrieve the transaction with the given ID
    transaction = Transaction.objects.get(id=pk)

    # Calculate the current value and ROI of the transaction
    current_val = transaction.get_current_value()
    roi = ((current_val - transaction.initial_value) / transaction.initial_value) * 100
    net_result = current_val - transaction.initial_value

    # Render the transaction template with data
    return render(
        request,
        "core/transaction.html",
        {
            "transaction": transaction,
            "current_val": current_val,
            "roi": roi,
            "net_result": net_result,
        },
    )


def login_user(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, ("You're now logged in."))
                return redirect("index")
        else:
            print(form.errors)
    else:
        form = CustomAuthenticationForm()

    if "next" in request.GET:
        messages.info(request, "Please log in to access the page.")

    return render(request, "core/login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, ("Account created. You've been logged in."))
            return redirect("index")
    else:
        form = CustomUserCreationForm()

    return render(request, "core/register.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.success(request, ("You've been logged out."))
    return redirect("index")


@login_required
def portfolio(request, pk):
    portfolio = Portfolio.objects.get(id=pk)
    metrics = PortfolioMetrics.objects.get(portfolio=pk)

    # CryptoCompare API endpoint for price data
    endpoint = "https://min-api.cryptocompare.com/data/price"

    # Parameters for the API request
    params = {
        "fsym": "BTC",  # From symbol (Bitcoin)
        "tsyms": "USD",  # To symbol (US Dollar)
        "api_key": api_key,
    }

    # Making the API request
    response = requests.get(endpoint, params=params)
    # Parse the JSON response
    data = response.json()
    # Extract the Bitcoin price in USD
    current_price = Decimal(data["USD"])
    current_value = metrics.BTC_amount * current_price
    print(f"CV: {current_value}")
    net_result = current_value - metrics.USD_invested
    current_ROI = ((current_value - metrics.USD_invested) / metrics.USD_invested) * 100

    if request.method == "POST":
        form = TransactionForm(request.POST or None)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.save()
            messages.success(request, ("Transaction Added"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        transactions = Transaction.objects.filter(portfolio=pk)
        metrics = PortfolioMetrics.objects.get(portfolio_id=pk)
        roi_data_dict = metrics.roi_dict

        # Create main and highlight data for the plot
        main_data = go.Scatter(
            x=[datetime.utcfromtimestamp(int(key)) for key in roi_data_dict],
            y=[Decimal(roi_data_dict[key]) for key in roi_data_dict],
            mode="lines",
            marker=dict(size=8),
            line=dict(color="grey", width=1),
            name="ROI",
        )

        highlight_data = go.Scatter(
            x=[datetime.utcfromtimestamp(t.daily_timestamp) for t in transactions],
            y=[roi_data_dict[str(t.daily_timestamp)] for t in transactions],
            text=[
                f"Amount: {t.amount} Cost: {t.initial_value:,.0f}$ Price: {t.price:,.0f}$".replace(
                    ",", " "
                )
                for t in transactions
            ],
            mode="markers",
            marker=dict(
                size=8,
                symbol="circle",
                color="#f7931a",
            ),
            name="Purchases",
        )

        # Define layout for the plot
        layout = go.Layout(
            title="Return On Investment In Time",
            xaxis=dict(
                title="Date",
                range=[
                    datetime.utcfromtimestamp(int(min(roi_data_dict.keys()))),
                    datetime.utcfromtimestamp(int(max(roi_data_dict.keys()))),
                ],
            ),
            yaxis=dict(title="ROI (%)", tickformat=".2f"),
            shapes=[
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=min(
                        [datetime.utcfromtimestamp(int(val)) for val in roi_data_dict]
                    ),
                    x1=max(
                        [datetime.utcfromtimestamp(int(val)) for val in roi_data_dict]
                    ),
                    y0=0,
                    y1=0,
                    line=dict(color="grey", width=1),
                )
            ],
            legend=dict(x=0.4, y=-0.2, traceorder="normal", orientation="h"),
            autosize=True,
        )

        # Create the plot
        fig = go.Figure(data=[main_data, highlight_data], layout=layout)

        # Convert the plot to HTML
        graph_html = fig.to_html(full_html=False)

        form = TransactionForm(request.POST or None)

        # Render the portfolio template with data
        return render(
            request,
            "core/portfolio.html",
            {
                "average_price": metrics.average_price,
                "current_ROI": current_ROI,
                "current_price": current_price,
                "current_value": current_value,
                "form": form,
                "graph_html": graph_html,
                "maxROI": metrics.max_roi[1],
                "maxROI_date": datetime.utcfromtimestamp(int(metrics.max_roi[0])),
                "minROI": metrics.min_roi[1],
                "minROI_date": datetime.utcfromtimestamp(int(metrics.min_roi[0])),
                "portfolio": portfolio,
                "net_result": net_result,
                "transactions": transactions,
                "metrics": metrics,
            },
        )
