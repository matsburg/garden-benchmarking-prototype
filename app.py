from calendar import month_abbr, day_name
import math

import streamlit as st
import pandas as pd
import altair as alt

# alt.renderers.enable("altair_viewer")


def price_hist(data, price_col, value, bin_width=2):

    hist = (
        alt.Chart(data)
        .mark_bar()
        .encode(x=alt.X(price_col, bin=alt.Bin(step=bin_width)), y="count()")
    )

    line = alt.Chart(pd.DataFrame({"x": [value]})).mark_rule(color="red").encode(x="x")

    return hist + line


def day_season_price_scatter(data, day_col, season_col, day_price, season_price):

    prices = data.loc[:, [day_col, season_col]]
    prices["highlight"] = False

    form_garden = pd.DataFrame(
        {day_col: [day_price], season_col: [season_price], "highlight": [True]}
    )
    prices_with_form_garden = pd.concat([prices, form_garden])

    scatter = (
        alt.Chart(prices_with_form_garden)
        .mark_point()
        .encode(
            x=day_col,
            y=season_col,
            color=alt.Color(
                "highlight",
                scale=alt.Scale(domain=[True, False], range=["red", "grey"]),
                legend=None,
            ),
        )
    )

    return scatter


def season_price_to_length_scatter(
    data, season_col, season_length_col, season_price, season_length
):
    plot_data = data.loc[:, [season_col, season_length_col]]
    plot_data["highlight"] = False

    form_garden = pd.DataFrame(
        {
            season_col: [season_price],
            season_length_col: [season_length],
            "highlight": [True],
        }
    )

    plot_data_with_form_garden = pd.concat([plot_data, form_garden])

    scatter = (
        alt.Chart(plot_data_with_form_garden)
        .mark_point()
        .encode(
            x=season_length_col,
            y=season_col,
            color=alt.Color(
                "highlight",
                scale=alt.Scale(domain=[True, False], range=["red", "grey"]),
                legend=None,
            ),
        )
    )

    return scatter


def open_days_bar_chart(form_garden_open_days):

    day_opening_pcts = pd.DataFrame(
        {
            "day": list(day_name),
            "pct_of_gardens_open": [0.3, 0.4, 0.6, 0.8, 0.86, 0.93, 0.96],
        }
    )

    day_opening_pcts["highlight"] = day_opening_pcts["day"].isin(form_garden_open_days)

    bars = (
        alt.Chart(day_opening_pcts)
        .mark_bar()
        .encode(
            x="pct_of_gardens_open",
            y=alt.Y("day", sort=list(day_name)),
            color=alt.Color(
                "highlight",
                scale=alt.Scale(domain=[True, False], range=["#1f77b4", "grey"]),
                legend=None,
            ),
        )
    )

    return bars


def month_highlight_bar(data, month_col, highlight_month):
    months = (
        data.loc[~data[month_col].isna(), :]
        .groupby(month_col)
        .size()
        .to_frame(name="gardens")
        .reindex(month_abbr, fill_value=0)
    )

    months["pct"] = months["gardens"] / months["gardens"].sum()
    months = months.reset_index()

    months["highlight"] = months[month_col].eq(highlight_month)

    bars = (
        alt.Chart(months)
        .mark_bar()
        .encode(
            x="pct",
            y=alt.Y(month_col, sort=list(month_abbr)),
            color=alt.Color(
                "highlight",
                scale=alt.Scale(domain=[True, False], range=["#1f77b4", "grey"]),
                legend=None,
            ),
        )
    )

    return bars


data = pd.read_csv("dummy_data.csv")
data["season_length"] = data["season_end_num"] - data["season_start_num"] + 1


st.title("Garden Benchmarking")

st.subheader("Input")
with st.form("input_form"):

    day_ticket_price = st.number_input(
        "Adult day ticket price (£)", min_value=0.00, value=10.00, format="%.2f"
    )

    season_ticket_price = st.number_input(
        "Adult season ticket price (£)", min_value=0.00, value=30.00, format="%.2f"
    )

    season_start, season_end = st.select_slider(
        "Season start and end",
        options=month_abbr[1:],
        value=(month_abbr[1], month_abbr[-1]),
    )

    season_start_num = list(month_abbr).index(season_start)
    season_end_num = list(month_abbr).index(season_end)
    season_length = season_end_num - season_start_num + 1

    if season_start == month_abbr[1] and season_end == month_abbr[-1]:
        season_type = "Year-round"
    else:
        season_type = "Seasonal"

    open_days = st.multiselect(
        "Typical open days during peak season", options=day_name, default=day_name
    )

    submitted = st.form_submit_button("Submit")

if submitted:
    # st.write(f"The season ticket price is {season_ticket_price}")
    # st.write(f"The day ticket price is {day_ticket_price}")
    # st.write(f"The garden opening season is {season_type}")
    # if season_type == "Seasonal":
    #     st.write(f"The season starts in {season_start} and ends in {season_end}")
    # st.write(f"Open on {', '.join(open_days)}")

    st.subheader("Price comparison")
    st.altair_chart(
        price_hist(data, "day_ticket_price", day_ticket_price)
        | price_hist(data, "season_ticket_price", season_ticket_price, 10)
    )

    st.subheader("Season ticket value")
    st.altair_chart(
        day_season_price_scatter(
            data,
            "day_ticket_price",
            "season_ticket_price",
            day_ticket_price,
            season_ticket_price,
        ),
        use_container_width=True,
    )

    season_to_day_ratio = season_ticket_price / day_ticket_price

    st.write(
        f"The season ticket is {season_to_day_ratio:.1f}x the price of the day ticket, which means a customer would need to visit {math.floor(season_to_day_ratio) + 1} times to benefit from purchasing a season ticket."
    )

    st.altair_chart(
        season_price_to_length_scatter(
            data,
            "season_ticket_price",
            "season_length",
            season_ticket_price,
            season_length,
        ),
        use_container_width=True,
    )

    st.write(
        f"The season ticket costs £{season_ticket_price/season_length:.1f} per month the garden is open per year"
    )

    if season_type == "Seasonal":
        st.subheader("Seasonal opening")
        st.altair_chart(
            month_highlight_bar(data, "season_start", season_start)
            | month_highlight_bar(data, "season_end", season_end),
            use_container_width=True,
        )

    st.subheader("Open days")
    st.altair_chart(open_days_bar_chart(open_days), use_container_width=True)
