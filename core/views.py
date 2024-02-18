# Standard library imports
from datetime import datetime, timezone
from decimal import Decimal

# Related third-party imports
import plotly.graph_objects as go
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import redirect, render, reverse

# Local application/library specific imports
from .forms import (
    CustomAuthenticationForm,
    CustomUserCreationForm,
    PortfolioForm,
    TransactionForm,
)
from .models import DailyClosePrice, Portfolio, PortfolioMetrics, Transaction
from .utils import get_current_price


@login_required
def index(request):
    """
    The index view for displaying and managing portfolios.

    - Fetches the current asset price using a utility function.
    - Retrieves all portfolios owned by the current user.
    - Allows the user to create a new portfolio through a form.
    - If the form is submitted and valid, a new portfolio is created and the user is redirected to the index page.
    - If there are no portfolios, renders an empty index template.
    - For users with portfolios, it calculates and displays overall investment metrics.
    """

    current_price = get_current_price()
    portfolios = Portfolio.objects.filter(user=request.user.id)
    form = PortfolioForm()

    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, "Portfolio Created")
            return redirect("index")

    else:
        if len(portfolios) == 0:
            return render(
                request,
                "core/index_empty.html",
                {"form": form, "current_price": current_price},
            )

        transactions = Transaction.objects.filter(portfolio_id__in=portfolios)
        metrics = PortfolioMetrics.objects.filter(portfolio__in=portfolios)
        overall = metrics.aggregate(Sum("USD_invested"), Sum("BTC_amount"))
        overall_current_value = (overall["BTC_amount__sum"] or 0) * current_price
        overall_net_result = overall_current_value - (overall["USD_invested__sum"] or 0)

    return render(
        request,
        "core/index.html",
        {
            "portfolios": portfolios,
            "form": form,
            "current_price": current_price,
            "transactions": transactions,
            "overall_invested": overall["USD_invested__sum"],
            "overall_net_result": overall_net_result,
        },
    )


@login_required
def transaction_view(request, pk):
    """
    Displays details of a specific transaction.

    Retrieves a transaction by its primary key (pk) and calculates its current value,
    return on investment (ROI), and net result based on the initial investment and
    current market price. It also formats the transaction timestamp for display.
    """

    transaction = Transaction.objects.get(id=pk)

    current_val = transaction.get_current_value()

    roi = ((current_val - transaction.initial_value) / transaction.initial_value) * 100

    net_result = current_val - transaction.initial_value

    time = datetime.utcfromtimestamp(transaction.timestamp_unix)
    time = time.replace(tzinfo=timezone.utc)

    return render(
        request,
        "core/transaction.html",
        {
            "transaction": transaction,
            "current_val": current_val,
            "roi": roi,
            "net_result": net_result,
            "time": time,
        },
    )


def login_user(request):
    """
    Handles the login process for users.

    If the request method is POST, it attempts to authenticate the user using the
    CustomAuthenticationForm. If authentication is successful, the user is logged in,
    a success message is displayed, and the user is redirected to the index page.
    If authentication fails, the form errors are printed to the console.

    For GET requests, or if authentication fails, the login form is displayed.
    If the 'next' parameter is present in the request, an informational message
    prompts the user to log in to access the requested page.
    """

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, "You're now logged in.")
                return redirect("index")
        else:
            print(form.errors)
    else:
        form = CustomAuthenticationForm()

    if "next" in request.GET:
        messages.info(request, "Please log in to access the page.")

    return render(request, "core/login.html", {"form": form})


def register(request):
    """
    Handles the user registration process.

    This view manages user registration using the CustomUserCreationForm. On POST requests, it
    attempts to create a new user account. If the form is valid, the user is saved, automatically
    logged in, and redirected to the index page with a success message. For GET requests, or if
    the form is not valid, it displays the registration form.
    """
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
    """
    Handles user logout process
    """
    logout(request)
    messages.success(request, ("You've been logged out."))
    return redirect("index")


def delete_portfolio(request, pk):
    """
    Deletes a specified portfolio if the request user is the owner.

    Retrieves the portfolio by its primary key (pk) and checks if the current
    user is the owner. If not, displays an authorization error message and redirects
    to the index page. If the user is the owner, the portfolio is deleted, a success
    message is displayed, and the user is redirected to the index page.
    """
    portfolio = Portfolio.objects.get(id=pk)
    if request.user.id != portfolio.user.id:
        messages.success(request, ("You are not authorized to do this!"))
        return redirect("index")
    portfolio.delete()
    messages.success(request, (f"Portfolio {portfolio.name} was deleted."))
    return redirect("index")


def delete_transaction(request, pk):
    """
    Deletes a specified transaction if the request user is the owner of the portfolio.

    This function retrieves the transaction by its primary key (pk) and checks if the current
    user is the owner of the portfolio containing the transaction. If not, it displays an
    authorization error message and redirects to the index page. If the user is the owner,
    the transaction is deleted. After deletion, it updates the portfolio metrics if there are
    remaining transactions, or deletes the portfolio metrics if there are none. A success message
    is displayed, and the user is redirected to the portfolio detail page.
    """
    transaction = Transaction.objects.get(id=pk)

    if request.user.id != transaction.portfolio.user.id:
        messages.success(request, ("You are not authorized to do this!"))
        return redirect("index")
    portfolio = Portfolio.objects.get(id=transaction.portfolio_id)
    transaction.delete()
    transactions = portfolio.transactions.all()
    if transactions:
        portfolio.update_metrics()

    else:
        metrics = portfolio.metrics
        metrics.delete()

    messages.success(request, (f"Transaction #{pk} was deleted."))
    return redirect(reverse("portfolio", kwargs={"pk": portfolio.id}))


@login_required
def portfolio(request, pk):
    """
    Displays and manages a specific portfolio identified by its primary key (pk).

    This view allows the authorized user to view details of their portfolio, add new transactions,
    and view the portfolio's performance metrics including a graph of Return On Investment (ROI) over time.

    Unauthorized users are redirected with an error message. The view supports both POST requests for
    adding new transactions and GET requests for viewing portfolio details. Metrics calculated include
    current value, net result, and current ROI. A Plotly graph visualizes the portfolio's ROI over time.
    """

    portfolio = Portfolio.objects.get(id=pk)
    current_price = get_current_price()

    if request.user.id != portfolio.user.id:
        messages.success(request, ("You are not authorized to view this!"))
        return redirect("index")

    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.portfolio = portfolio
            transaction.save()
            messages.success(request, ("Transaction Added"))
            return redirect(request.META.get("HTTP_REFERER"))
        return render(request, "core/portfolio.html", {"form": form})

    else:
        transactions = Transaction.objects.filter(portfolio=pk).order_by(
            "daily_timestamp"
        )
        if len(transactions) == 0:
            form = TransactionForm()

            return render(
                request,
                "core/portfolio_empty.html",
                {"form": form, "portfolio": portfolio},
            )

        metrics = PortfolioMetrics.objects.get(portfolio_id=pk)
        current_value = metrics.BTC_amount * current_price
        net_result = current_value - metrics.USD_invested
        current_ROI = (
            (current_value - metrics.USD_invested) / metrics.USD_invested
        ) * 100
        roi_data_dict = metrics.roi_dict

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

        fig = go.Figure(data=[main_data, highlight_data], layout=layout)

        graph_html = fig.to_html(full_html=False)

        form = TransactionForm()

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
