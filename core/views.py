from datetime import datetime
from decimal import Decimal
import cryptocompare
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, PortfolioForm
from .models import DailyClosePrice, Transaction, Portfolio
from .forms import TransactionForm


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
        print(request.GET)
        print(type(request.GET))
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
    # Retrieve current BTC price
    current_price = Decimal(cryptocompare.get_price("BTC", "USD")["BTC"]["USD"])

    # Fetch all transactions for a specific portfolio, ordered by timestamp
    portfolio = Portfolio.objects.get(id=pk)
    transactions = Transaction.objects.filter(portfolio__id=portfolio.id).order_by(
        "timestamp"
    )
    print(f"T{transactions}")
    print(type(transactions))
    if request.method == "POST":
        form = TransactionForm(request.POST or None)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.save()
            messages.success(request, ("Transaction Added"))
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        # Aggregate transaction data
        transactions_data = transactions.aggregate(
            amount=Sum("amount"),
            cost=Sum("initial_value"),
        )

        # Find the start date of the transactions
        start_date = transactions.first().daily_timestamp

        # Retrieve daily close prices from the start date
        data = DailyClosePrice.objects.filter(daily_timestamp__gte=start_date)

        # Initialize variables
        roi_data_dict = {}
        average_price = None
        current_value = transactions_data["amount"] * current_price

        # Calculate ROI data for each day
        for day in data:
            cumulative_data = transactions.filter(
                timestamp_unix__lte=day.daily_timestamp
            ).aggregate(
                amount_cumulative=Sum("amount") or Decimal("0"),
                value_cumulative=Sum(
                    ExpressionWrapper(
                        F("amount") * F("price"), output_field=DecimalField()
                    )
                ),
                average_price=ExpressionWrapper(
                    F("value_cumulative") / F("amount_cumulative"),
                    output_field=DecimalField(),
                ),
                roi=ExpressionWrapper(
                    ((day.close_price - F("average_price")) / F("average_price")) * 100,
                    output_field=DecimalField(),
                ),
            )

            # Store ROI data for each day
            roi_data_dict[day.daily_timestamp] = cumulative_data["roi"] or Decimal("0")
            average_price = cumulative_data["average_price"]
            current_value = transactions_data["amount"] * current_price

        # Calculate net result and current ROI
        net_result = current_value - transactions_data["cost"]
        current_ROI = (
            (current_value - transactions_data["cost"]) / transactions_data["cost"]
        ) * 100

        # Find dates with minimum and maximum ROI
        minROI = min(roi_data_dict.items(), key=lambda x: x[1])
        maxROI = max(roi_data_dict.items(), key=lambda x: x[1])

        # Create main and highlight data for the plot
        main_data = go.Scatter(
            x=[datetime.utcfromtimestamp(val) for val in roi_data_dict],
            y=[roi_data_dict[val] for val in roi_data_dict],
            mode="lines",
            marker=dict(size=8),
            line=dict(color="grey", width=1),
            name="ROI",
        )
        highlight_data = go.Scatter(
            x=[datetime.utcfromtimestamp(t.daily_timestamp) for t in transactions],
            y=[roi_data_dict[t.daily_timestamp] for t in transactions],
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
                    datetime.utcfromtimestamp(min(roi_data_dict.keys())),
                    datetime.utcfromtimestamp(max(roi_data_dict.keys())),
                ],
            ),
            yaxis=dict(title="ROI (%)", tickformat=".2f"),
            shapes=[
                dict(
                    type="line",
                    xref="x",
                    yref="y",
                    x0=min([datetime.utcfromtimestamp(val) for val in roi_data_dict]),
                    x1=max([datetime.utcfromtimestamp(val) for val in roi_data_dict]),
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
                "average_price": cumulative_data["average_price"],
                "cost": transactions_data["cost"],
                "current_ROI": current_ROI,
                "current_amount": transactions_data["amount"],
                "current_price": current_price,
                "current_value": current_value,
                "form": form,
                "graph_html": graph_html,
                "maxROI": maxROI[1],
                "maxROI_date": datetime.utcfromtimestamp(maxROI[0]),
                "minROI": minROI[1],
                "minROI_date": datetime.utcfromtimestamp(minROI[0]),
                "portfolio": portfolio,
                "net_result": net_result,
                "transactions": transactions,
            },
        )
