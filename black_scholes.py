import math
from scipy.stats import norm
from scipy.optimize import fsolve

def calculate_black_scholes(S, K, T, r, option_price, option_type):
    """Calculate implied volatility and Greeks using the Black-Scholes model."""

    def d1(S, K, T, r, sigma):
        return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

    def d2(S, K, T, r, sigma):
        return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

    # Initial guess for implied volatility
    sigma = 0.2  # Starting assumption for volatility
    tol = 1e-6  # Tolerance level for Newton-Raphson method
    max_iter = 100

    # Newton-Raphson method to find implied volatility
    for _ in range(max_iter):
        d_1 = d1(S, K, T, r, sigma)
        d_2 = d2(S, K, T, r, sigma)

        if option_type == "call":
            price = S * norm.cdf(d_1) - K * math.exp(-r * T) * norm.cdf(d_2)
            vega = S * norm.pdf(d_1) * math.sqrt(T)
        else:  # Put option
            price = K * math.exp(-r * T) * norm.cdf(-d_2) - S * norm.cdf(-d_1)
            vega = S * norm.pdf(d_1) * math.sqrt(T)

        diff = price - option_price

        if abs(diff) < tol:
            break

        sigma -= diff / vega  # Adjusting volatility

    # Compute Greeks
    delta = norm.cdf(d_1) if option_type == "call" else norm.cdf(d_1) - 1
    gamma = norm.pdf(d_1) / (S * sigma * math.sqrt(T))
    theta = (-(S * norm.pdf(d_1) * sigma) / (2 * math.sqrt(T)) - r * K * math.exp(-r * T) * norm.cdf(d_2)) / 365  # Per day
    vega = S * norm.pdf(d_1) * math.sqrt(T)
    win_rate = norm.cdf(d_1)
    optimal_risk = (win_rate - (1 - win_rate)) / 1  # Simplified Kelly Criterion

    return {
        "Implied Volatility": sigma * 100,  # Convert to percentage
        "Delta": delta,
        "Gamma": gamma,
        "Theta": theta,
        "Vega": vega,
        "Win Rate": win_rate,
        "Optimal Risk (Kelly)": optimal_risk,
        "sigma": sigma  # Add raw sigma for use in required_stock_price
    }

def required_stock_price(S_initial, K, T_initial, r, option_price, sigma, option_type, days_later):
    """Calculate the required stock price after 'days_later' to maintain the same option price."""
    T_new = T_initial - (days_later / 365)  # Remaining time in years

    def bs_price_diff(S_new, K, T_new, r, sigma, option_price, option_type):
        d_1 = (math.log(S_new / K) + (r + 0.5 * sigma ** 2) * T_new) / (sigma * math.sqrt(T_new))
        d_2 = d_1 - sigma * math.sqrt(T_new)
        if option_type == "call":
            price = S_new * norm.cdf(d_1) - K * math.exp(-r * T_new) * norm.cdf(d_2)
        else:  # Put option
            price = K * math.exp(-r * T_new) * norm.cdf(-d_2) - S_new * norm.cdf(-d_1)
        return price - option_price

    # Use fsolve to find S_new
    S_new = fsolve(bs_price_diff, S_initial, args=(K, T_new, r, sigma, option_price, option_type))[0]
    avg_daily_move = (S_new - S_initial) / days_later if days_later > 0 else 0

    return {
        "Required Stock Price": S_new,
        "Average Daily Move": avg_daily_move
    }