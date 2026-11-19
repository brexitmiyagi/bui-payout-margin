# bui-payout-margin

This is the data and code behind my Seeking Alpha piece on BlackRock Utilities, Infrastructure & Power Opportunities Trust (BUI), November 2026: "BUI: The Fee Is Certain, Here's Where Last Year's Edge Came From", and my X thread on utilities losing their stock-market beta in 2026.

The short version: in 2026 utilities lost their link to the stock market and kept their rate risk. BUI's NAV has about 8 years of effective rate duration this year (range 6 to 10.5), close to a 10-year Treasury note, while it pays 7.15% of NAV (November 18) from a book yielding about 2.8%. The target is built from 10-year scenarios. The Section 19 coverage number has a weak spot at December 31, 2026 and then gets lifted by base effects through 2027.

Plain Python 3. The newer scripts and rate_beta_tests.py need numpy, pandas and statsmodels (pip install numpy pandas statsmodels). The older ones run on the standard library.

## How to run it

From anywhere:

    python scripts/payout_hurdle.py

Each script reads from data/ relative to itself and prints to the screen. My own output is saved in results/.

## What each script does

scripts/latest_close.py prints the numbers in the post that move with the price, at the November 18 close: BUI's 0.35% discount, the target ($25.86), trim ($26.12), accumulate ($24.57) and Buy ($22.50) levels, the 7.15% payout on NAV, the four funds' yields on price and discounts, and the UTF-BUI spread (-7.09) against its one-year median (-5.33).

scripts/chart_data.py and scripts/technical_charts.py write the data behind the line charts: BUI's premium since 2016 with the +1% trim line, the premium through the rights offering against UTF, the cumulative NAV gap, the rolling 52-week rate beta with a 95% Newey-West band, the premium's z-score against its 60-day average, and the NAV fan to December 2027 (same 20,000 draws as payout_cut_probability.py).

scripts/pair_exit_backtest.py tests the UTF/BUI pair with the exit rule the post states (exit when the spread is back at its one-year median, or after 12 months): 13 trades since 2016, 12 won, average +4.9 points over about 31 trading days, before roughly 1.4 points of spread costs and borrow.

scripts/after_tax_yield.py compares BUI's after-tax yield and annual tax drag with XLU's for a taxable US holder, using BUI's 2025 qualified-dividend designation (85% of ordinary dividends), the 2026 Section 19 mix, XLU's 2025 tax summary (100% qualified) and 2026 federal rates. Top bracket: BUI about 4.8% after tax on this year's mix against XLU's 2.1%; tax paid each year about 2.2 points of price against 0.7. That's tax paid, not tax cost, see after_tax_wealth.py.

scripts/after_tax_wealth.py holds BUI and XLU for 5 and 10 years on the same book, taxes each distribution in the year it's paid, reinvests the rest and taxes the gain at the sale. Top bracket, this year's mix, five years: BUI's real tax cost is about 0.66 points a year (0.16 on 2025's mix), and with the fee gap BUI trails XLU by about 1.45 points after tax. It also gives the discount at purchase that leaves BUI level with XLU at the end, selling at NAV: about 4.4% in an IRA, 6.2% in the 24% bracket and 7.9% in the top bracket over five years, roughly double over ten.

scripts/holdings_lookthrough.py groups the June 30, 2026 N-PORT into buckets (my grouping, in data/holding_buckets.csv) and lists BlackRock's October 30 top ten: US regulated utilities 40.2%, pipelines and LNG 13.8%, rail, airports and toll roads 10.2%, top ten 43.0%.

scripts/attribution.py splits BUI's year since dropping covered calls into sector bets, stock picks and the 2026 IPOs, from the December, March and June N-PORTs, against the five-year book-like ETF mix, December 31, 2025 to November 13, 2026. The seven weeks before that are left out because the book was rebuilt then (147 positions to 49). Price only on both sides. Holdings +9.6% against +8.1% for the mix; sector bets -1.1 points, stock picks +3.4 (best: Cheniere, Targa, Union Pacific), IPOs -0.4. A daily test on the US-listed names puts stock picks at +4.5% a year with 4.2% tracking error, t = 1.0.

scripts/nav_gap.py works on the NAV return the quarter-end books can't explain. In the half to June 30 the N-CSRS shows $4.07 a share of gains against $3.56 for the December book held untouched, so $0.51 (2.1% of NAV) a buy-and-hold book can't produce. Because that per-share line is partly a balancing figure and BUI issued 2.4m shares in April, it redoes the check in dollars from the statement of operations, adding the $64.7m of rights money at the book's return from April 2: $100.2m of gains against $85.5m buy-and-hold, a $14.7m gap (about $0.58 a share). That's consistent with trading gains between quarter-ends, not proof of skill; turnover was 23%, securities lending $1,406, tax reclaims about 0.04%, and the rights offering cost $0.10. There's no sign of late foreign marks (yesterday's S&P on today's NAV residual: 0.015, t = 1.0), and the gap arrives on a handful of days.

scripts/rights_offering.py follows BUI's premium through the 2026 rights offering: +8.9% at the February 27 announcement, -5.1% at the April 2 expiration, when the 95%-of-NAV floor set the subscription price at $26.37 against a $26.34 close. About 40% of the offer was taken.

scripts/cef_connect_timing.py compares CEF Connect's live discounts from the evening of November 13 with its own final history for the same day. The snapshot was off by more than a quarter point for 29 of 106 funds; BUI showed -0.33% live and -0.64% final.

scripts/premium_patterns.py tests whether BUI's premium is tradable: it snaps back (half-life about 16 days) but a five-day rule makes 0.72 points before a 0.8 round trip; since dropping calls the price lags the NAV by a day (coefficient 0.27, t = 3.5), worth 0.42 points the next day after big gaps; regular ex-dates do nothing, and the December 2025 special pushed the premium from +2.7% to +7.2%.

scripts/issuance_vs_premium.py lines up the dated share counts with premium days: 496,220 new shares from June 30 to November 13 against 34 days at a +1% premium or more, none since October 29. The daily log I keep of BlackRock's share count will test it day by day.

scripts/valuation_same_basis.py compares BUI's US-listed names (75% of net assets) with XLU rebuilt from the 31 S&P 500 utilities, both on Nasdaq consensus EPS for the fiscal year nearest December 2027. Without the 2026 IPOs: BUI 17.0 times with 8.6% growth the year after, XLU 16.6 times with 9.6%.

scripts/payout_cut_probability.py puts a probability on a cut to the $0.154 monthly payout by December 2027, with the trigger set from what BlackRock has done (BUI paid 8.1% of NAV in March 2020 without cutting). At that trigger, a NAV under $22.81 at two quarter-ends in a row, 3.5% to 6.1% of paths, depending on whether the returns come from every month since 2016 or the last five years; at 7.5% of NAV, 27% to 33%.

scripts/cef_vs_etf_screen.py runs the same vehicle question across 108 equity CEFs for a tax-deferred account: the discount that pays for five years of the fee gap, and what you earn each year if the discount never closes. 28 pass both tests, 39 fail both, BUI fails both.

scripts/style_analysis.py is the main edge test. Constrained style regressions (weights non-negative, summing to 100%) of weekly NAV total returns for BUI, UTF, DNP and GLU on two ETF sets: book-like (XLU, IGF, AMLP, XLI, IEF) and total-return clean (IGF, PUI, GRID, IEF), with 8-week block bootstrap bands and the years of data needed to reach t = 2. BUI over the last five years: -1.6% a year after fees (book-like, band -5.0 to +1.6) and -1.0% (clean); 34 to 71 years of data to settle it.

scripts/vehicle_table.py puts BUI, UTF, DNP, GLU, XLU and IGF side by side: costs before and with leverage, on one basis from each fund's latest report, yield, premium or discount, 2026 rate beta on one model, edge, and median daily dollar volume.

scripts/target_band.py simulates the target inputs (10-year move at option-implied volatility, duration, growth, non-rate return, premium): median $26.58, 10th to 90th percentile $21.47 to $31.78.

scripts/position_pnl.py gives the one-year P&L on $100,000 of BUI for 10-year moves of -100 to +100bp, unhedged at durations of 6, 8 and 10.5 and hedged with 10-year notes, plus sizing for a 1% volatility budget. Illustrative, not advice.

scripts/switch_oos.py picks the UTF switch threshold on 2016-2020 only and tests it from 2021 on.

scripts/tax_character.py shows the tax character of BUI's distributions: 2023-2025 final, 2026 estimated (about 44% at ordinary rates so far if income is 85% qualified as in 2025, against 3% in 2025).

scripts/etf_replication.py answers "why not the ETF". It regresses BUI's weekly NAV total return on IGF and IEF total returns (Nasdaq distributions, IGF tied to iShares' published returns within 0.01 points). Alpha after BUI's fees: +3.2% a year over the whole sample (t 1.7), almost all in the covered-call era; -1.3% over the last five years (t -0.5); +0.8% since the calls ended (t 0.2).

scripts/valuation_lookthrough.py puts XLU's forward earnings yield (5.48%) against the 10-year (5.15%), tracks the income yield of BUI's own book against the 10-year by year (+0.6 points in 2021, about -2.3 now), and shows the target at FactSet's 9.42% growth ($27.01) against my 7% ($26.38).

scripts/platform_issuance.py lines up BlackRock's shelf sales by equity CEF and year (2023 to mid-2026) against how often each fund traded at a premium.

scripts/fed_path.py reads the Fed path out of the November 13 Treasury curve (about 100bp of tightening from 1-month bills to the 1y1y forward).

scripts/issuance_test.py checks whether BlackRock actually sells BUI shares into the premium and whether that caps it. Shares outstanding rose 496,220 (1.87%) from June 30 to November 13; the shelf sold 1,373,141 shares in 2025 and none in the first half of 2026. 2025 sold at about the same monthly pace as since July and the premium still averaged about 2%, so selling trims the premium rather than capping it.

scripts/discount_own_history.py compares BUI's discount with its own history since 2017 (monthly, on its distribution rate, the 10-year and its trailing NAV return). That levels regression overstates the 10-year link (the 10-year has a unit root, p 0.91), so the script also runs changes on changes: about -1.5 points of discount per 1-point rise in the 10-year monthly (t -1.4) and -1.9 weekly (t -2.2), explaining about 1% of moves. The post treats it as a weak, same-signed nudge.

scripts/switch_backtest.py is the UTF switch test. It flags every day since November 2016 when UTF's discount minus BUI's was 5 or more points below its own trailing one-year median and measures UTF minus BUI total return over the next 12 months (12 episodes, UTF won 9, average +9.6 points; all signal days 73% hit rate and +5.6 points against 57% and -0.7 on all days; block bootstrap about 0.11). It also fits weekly half-lives for each discount and the spread (BUI about 4 weeks, UTF and the spread about 7 to 8), the mid-November to year-end and January seasonality, and BUI's premium before and since the July 1 at-the-market supplement.

scripts/premium_lid.py compares premiums before and after the 2026 at-the-market supplements for BUI, CII and BST, against 20 control funds. issuance_test.py supersedes its conclusion: the premium fell after July, but the issuance data say selling isn't what capped it.

scripts/nav_rebuild.py rebuilds BUI's NAV daily from the June 30 N-PORT for the 32 listed names (74.7% of net assets, R-squared 0.92 against the reported NAV, -2.18% against -2.83% reported from June 30 to November 13) and checks daily against weekly rate betas for BUI's NAV, XLU and SPY.

scripts/discount_screen.py regresses the discount of 108 equity CEFs on distribution rate, NAV return, leverage, size and expenses, and ranks the utility and energy-infrastructure funds by what the model doesn't explain (BUI +9.8 points rich, UTF +1.8).

scripts/section19_platform.py ranks BUI's Section 19 gap among BlackRock's equity trusts, puts UTF's own notice next to it (-0.57), and shows how often the final tax character included return of capital, 2023 to 2025.

scripts/implied_rate_vol.py turns one-year IEF option implied volatility into a 10-year yield volatility (about 1.06 points) and reruns the scenario target with it ($25.83 at the November 18 close, the same as with historical volatility). These are the scenarios in the post's rate table.

scripts/technicals_liquidity.py gives discount z-scores and momentum, moving averages and RSI, volume around ex-dates and the rights offering, average daily dollar volume, how long a $5 million position takes at 15% of volume, and an Abdi-Ranaldo spread estimate.

scripts/nport_book.py reads BUI's quarterly N-PORT filings: positions and written calls each quarter (147 positions with 94 written calls at September 30, 2025, 49 and none at December 31), monthly NAV returns, and realised gains by quarter including the $61.1m in Q4 2025.

scripts/realised_vs_paid.py gives income plus realised gains against distributions for 2025 and the first half of 2026 (2.37x in H1 2026, income alone 28%), shares outstanding since June 30, and what the rights offering adds to the advisory fee.

scripts/margin_path.py rebuilds the Section 19 margin for month-ends the notices haven't covered yet (about +1.06 points at October 30) and shows what NAV total return between now and March 31, 2027 would take the margin below zero (about -4%).

scripts/rate_sensitivity.py regresses weekly NAV total return on the weekly change in the 10-year yield, year by year (-8.6% per +100bp in 2026, -6.5% since June 30).

scripts/june_book_replay.py replays the June 30, 2026 holdings for the 32 US and Canada listed names to the November 13 close (growth and equipment -$0.53 a share, utilities and the rest -$0.44, pipelines and railroads +$0.41).

scripts/peers_relative_value.py runs the same tests on UTF, DPG and GLU: discount now against each fund's own history, distribution rate, the 5-year NAV return minus payout gap (rebuilt from Nasdaq NAVs and distributions, tied out to each fund's reported returns within 0.15 points), and 2026 rate and equity betas. Balance-sheet items are in data/peer_fundamentals.csv with sources.

scripts/hypothesis_ai_premium.py tests whether the utilities that rallied most in 2025 lost the most equity beta in 2026. Across 34 names, every one lost beta, but the rank correlation with 2025 return is only -0.11 (permutation p = 0.27), so the drop was sector-wide.

scripts/state_exposure.py maps BUI's June 30 utility holdings to states with new political pressure on utilities (21.1% of net assets), with the subsidiary named in each 10-K or 20-F.

scripts/stress_test.py applies a 10-year +150bp and equal-weight S&P -17.5% shock to today's NAV under 2026 and 2022 sensitivities.

scripts/rate_beta_tests.py is the main statistics file. Weekly regressions with Newey-West (HAC, 4 lags) standard errors for BUI's NAV, XLU and the NAVs of UTF, UTG and DNP, on the 10-year change plus the S&P 500, the equal-weight S&P 500 (RSP), semiconductors (SMH) and oil (USO). It also tests 2026 against each earlier year, runs rolling 26-week betas with 95% bands (written to results/rolling_rate_beta.csv), Dimson daily betas for BUI, and the XLU-SPY correlation with a 95% interval.

scripts/duration_and_valuation.py turns the betas into an effective duration (central 8, range 6 to 10.5), compares it with the 10-year note (7.77 at 5.07%), gives the hedge ratio (about $103 of 10-year notes per $100 of BUI), the hedged volatility and carry, and the $25.83 target from 10-year scenarios at the November 18 close. The hedged return is about +8.0% a year (corrected 16 Nov 2026, see Corrections).

scripts/target.py is the older history-based target ($27.09). I keep it as a cross-check.

scripts/regime_shift.py regresses weekly and daily returns on the 10-year yield change and the S&P 500 together, year by year, for XLU and BUI's NAV. In 2026 XLU's S&P beta is about zero (-0.23 weekly) and its weekly correlation with SPY -0.10, against +0.57 in 2025. BUI's NAV loses about 8.7% per +100bp, its most since 2017.

scripts/section19_base_effects.py runs the Section 19 margin forward to December 2027 at flat, 5% and 8.28% NAV returns, shows which 2021-2022 months leave the 5-year window, finds the NAV move that turns the December 31, 2026 margin negative (about -3%, or -2.5% with a $0.50 special) and how often BUI has fallen that much in 32 trading days.

scripts/payout_simulation.py resamples 12-month blocks of BUI's monthly NAV returns three years forward at the current payout: about a 36% chance the margin goes negative at some month-end by December 2027.

scripts/discount_event_study.py compares discounts before BlackRock announced the end of call writing and now, for the seven funds that dropped it, the four BlackRock funds that kept options, and 97 other equity CEFs.

scripts/ipo_sleeve.py covers the three 2026 IPO names in the June book (SpaceX, Fervo Energy, SOLV Energy): IPO price, June 30 and November 13 values, about -$0.25 a BUI share if still held. Valued at their IPO prices, the three were worth about $0.8 million less on November 13 (-0.11% of June 30 net assets), so they don't explain BUI's strong year since dropping calls.

scripts/blackrock_platform.py puts BUI next to the rest of BlackRock's CEF platform: seven rights offerings since June 2025 (about $1.0bn raised), SpaceX at 3.0-3.1% of net assets in four BlackRock CEFs, what the seven funds that dropped call writing did with their payouts, and how fast the rights offering fee pays back BlackRock's costs (about 5.5 months).

scripts/payout_hurdle.py gives the 7.15% hurdle at the November 18 NAV, the 2,265 rolling 12-month NAV return windows since November 2016, the 61% of them that cleared the hurdle, the 17.1% that were negative, the histogram buckets, and the 10-year and 5-year annualized NAV return.

scripts/section19_margin.py gives the month by month gap (and flags the $0.104 a share drop in year to date short-term gains between the September and October notices) between the 5-year NAV return and the distribution rate, straight from the notices, plus the fiscal year to date payout mix (30% income, 40% short-term gains, 30% long-term gains).

scripts/nii_coverage.py gives net income against distributions from 2021 to the first half of 2026, the 25% coverage figure, and the $1.88 a share of return of capital paid from 2021 to 2024.

scripts/precedent.py replays 2021 to 2024 (5.25% a year NAV return, NAV down 4.8%) and runs the same four years from today's NAV at today's payout ($24.37).

scripts/gains_reservoir.py gives the $7.89 a share of unrealized gain at June 30 and my estimate of about $6.34 now.

scripts/since_raise.py gives NAV, price and XLU since June 30, and the August and September month-end NAV.

scripts/premium.py gives the premium/discount history (median +0.56%, the 2026 high of +10.28% on March 5, and the latest -0.35% on November 18).

scripts/target.py gives the three scenarios and the $27.09 target.

scripts/tieout.py is the check on my NAV return rebuild, see below.

scripts/common.py loads the data and builds the NAV total return index. Distributions get reinvested at NAV on the ex-date.

## Checking my NAV return against BlackRock's

I rebuilt the NAV total return myself instead of taking it from anyone. scripts/tieout.py checks it against what BlackRock publishes and stops if any gap goes over 0.15 points. It comes out at 8.00% a year for the 5 years to September 30 against the fund's 8.05%, 5.83% for 2026 to September 30 against 5.83%, and 17.24% for the first half of 2026 against the semi-annual report's 17.18%. The small gaps come from the timing of the reinvestment.

## Data

data/bui_price_nav_daily.csv has BUI's close, BUI's NAV (Nasdaq symbol XBUIX), XLU and SPY, daily from November 14, 2016 to November 13, 2026. Pulled from Nasdaq's historical quotes.

data/bui_distributions.csv has every distribution with ex, record and pay dates and the tax character, from BlackRock's BUI product page.

data/section19_notices_2026.csv is my transcription of the nine Section 19 notices from February 27 to October 30, 2026, with the link to each PDF.

data/financial_highlights.csv is the per share table from the semi-annual report for the six months to June 30, 2026.

data/nport/ has the five N-PORT filings as SEC published them (quarters ending June 2025 to June 2026).

data/listed_holdings_prices.csv has the June 30 and November 13, 2026 closes for the 32 listed holdings, from Nasdaq's historical quotes.

data/dgs10.csv is the 10-year Treasury yield from FRED. data/treasury_par_curve_2026.csv is Treasury's daily par yield curve for 2026.

data/statement_totals.csv has income, realised gains, distributions and new capital from the semi-annual report's statements.

data/peer_cefs_2026_11_13.csv is CEF Connect's premium/discount, distribution rate on NAV and year to date NAV return for BUI and its utility and infrastructure peers on November 13, 2026. CEF Connect's BUI NAV ($26.45) differs from BlackRock's ($26.38). I use BlackRock's everywhere else.

data/blackrock_rights_offerings_2025_2026.csv lists the BlackRock CEF rights offering results I found on EDGAR since June 2025, with links. data/spacex_across_blackrock_cefs_2026_06_30.csv is SpaceX in each BlackRock CEF schedule at June 30, 2026. data/sibling_regular_payouts.csv is the regular payout history of the seven funds that dropped call writing on November 10, 2025, from CEF Connect and BlackRock.

data/discount_event_study_fund_windows.csv and data/discount_monthly_blackrock_vs_others.csv are averages I computed from CEF Connect's weekly premium/discount history for 120 equity CEFs, pulled on November 16, 2026. The weekly series runs to November 6, 2026. I didn't keep the raw weekly file for all 120 funds, so these two files are the averages, not the raw data.

data/factors_and_peer_navs_daily.csv has daily closes for RSP, SMH and USO and the daily NAVs of UTF (XUTFX), UTG (XUTGX) and DNP (XDNPX) from Nasdaq, November 2016 to November 13, 2026.

data/peer_distributions.csv has UTF, GLU and DPG distribution histories from CEF Connect. data/us_utilities_daily_2025_2026.csv has daily closes for 34 US utilities and power producers from Nasdaq.

data/equity_cef_universe_2026_11_13.csv is CEF Connect's discount, distribution rate on NAV, one-year NAV return, leverage, total assets and expense ratio for 108 equity CEFs on November 13, 2026. data/cef_discount_zscores_1y_2026_11.csv is one-year discount statistics I computed from CEF Connect's daily history for 24 funds.

data/blackrock_atm_premium_test_2026.csv and data/control_cef_mean_discount_split_2026_07_01.csv are premium statistics I computed from CEF Connect's daily history, one year to November 12, 2026.

data/listed_holdings_daily_2026h2.csv has daily closes from June 26 to November 13, 2026 for the 32 listed holdings, from Nasdaq.

data/bui_ohlcv_daily.csv and data/utf_ohlcv_daily.csv are daily open, high, low, close and volume from Nasdaq. data/ief_daily.csv is IEF's daily close from Nasdaq. data/ief_options_cboe_2026_11_13.json is Cboe's delayed IEF option chain as of the November 13 close.

data/blackrock_section19_2026_10_30.csv is my transcription of the equity trusts in BlackRock's October 30, 2026 Section 19 notice. data/blackrock_tax_character_2023_2025.csv is the "tax character of distributions paid" tables from BlackRock's 2024 and 2025 annual reports. data/utf_events_2019_2026.csv lists UTF's corporate events with links.

data/etf_prices_daily.csv and data/etf_distributions.csv are XLU, IGF and IEF closes and IGF and IEF distributions from Nasdaq. XLU's dividend history isn't on Nasdaq, so XLU enters the replication as a price return only. data/valuation_snapshot_2026_11_13.csv has the State Street and iShares figures with links. data/blackrock_shelf_issuance_2023_2026.csv and data/blackrock_weekly_premium_by_year.csv are the platform issuance dataset.

data/vehicle_prices_volumes_daily.csv has DNP and GLU closes and volumes and XLU and IGF volumes from Nasdaq. etf_prices_daily.csv now also has AMLP, XLI, PUI and GRID; etf_distributions.csv adds PUI and GRID. peer_distributions.csv adds DNP's monthly $0.065 from CEF Connect.

data/listed_holdings_daily_2025_2026.csv has Nasdaq daily closes for every US-listed name BUI held at December, March or June, November 2025 to November 2026. data/proxy_etf_prices_daily.csv has the bucket ETFs not already in etf_prices_daily.csv (JXI, MLPX, ICLN, XLB). data/holdings_map.csv maps each holding's ISIN to its US ticker and my bucket. data/consensus_eps_2026_11_18.csv is the Nasdaq consensus EPS snapshot, and data/sp500_utilities_2026_11.csv the 31 S&P 500 utilities from Wikipedia's S&P 500 list. data/category_etf_fees_2026_11.csv has the matching ETF and its fee for each CEF category, with links. data/cef_connect_history_2026_11_18.csv has each fund's final November 13 discount and latest close from CEF Connect's pricing history. data/cef_discounts_2026_11_18.csv has the November 18 close and NAV from Nasdaq for the 83 funds that had posted a NAV, and CEF Connect's November 17 figures for the other 25; on November 17 the Nasdaq and CEF Connect discounts matched for all 78 funds I could compare. data/close_2026_11_18.csv has the November 18 closes, NAVs and monthly distributions for BUI, UTF, DNP and GLU. data/treasury_par_curve_2026.csv and data/dgs10.csv now run to November 18. data/bui_rights_offering_2026.csv has the rights offering terms and results with SEC links.

data/us_tax_rates_2026.csv has the 2026 federal rates with IRS sources. data/qualified_dividend_designations_2025.csv has BUI's and XLU's 2025 qualified dividends. data/bui_borrow_2026_11_16.csv is the borrow fee and availability for shorting BUI (IBorrowDesk, from Interactive Brokers).

## Sources

BUI semi-annual report (N-CSRS), June 30, 2026: https://www.sec.gov/Archives/edgar/data/1528988/000119312526381618/d311167dncsrs.htm

BUI annual report (N-CSR), December 31, 2025: https://www.sec.gov/Archives/edgar/data/1528988/000119312526093831/d32962dncsr.htm

Rights offering terms, February 27, 2026: https://www.sec.gov/Archives/edgar/data/1528988/000119312526083074/d110238d497ad.htm

Rights offering result, April 2026: https://www.sec.gov/Archives/edgar/data/1528988/000119312526140992/d123774d497ad.htm

Shelf prospectus supplement, July 1, 2026: https://www.sec.gov/Archives/edgar/data/1528988/000119312526292709/d155913d424b2.htm

Section 19 notices: links are in data/section19_notices_2026.csv. The latest is https://www.blackrock.com/us/individual/literature/tax-information/section-19-october-30-2026.pdf

BlackRock BUI page: https://www.blackrock.com/us/individual/products/240173/blackrock-utilities-infrastructure-power-opportunities-trust

Nasdaq historical quotes: https://www.nasdaq.com/market-activity/stocks/bui/historical

BlackRock release on dropping the call writing, September 10, 2025: https://www.businesswire.com/news/home/20250910633094/en/Certain-BlackRock-Sector-Equity-Closed-End-Funds-Announce-Updates-to-Investment-Objectives-and-Principal-Investment-Strategies

N-PORT filings: https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001528988&type=NPORT-P

FRED 10-year yield: https://fred.stlouisfed.org/series/DGS10

Treasury par yield curve: https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026

CEF Connect: https://www.cefconnect.com/fund/BUI

Gabelli Funds, Utilities - U.S., June 26, 2026: http://gabelli.com/wp-content/uploads/2026/06/Utility-Outlook-6-30-2026-A.pdf

S&P Global RRA, Quarterly update on decided rate cases, June 2026 (filed with the Utah PSC): https://pscdocs.utah.gov/electric/24docs/2403504/346077DPUExhbt1S&PGlblMjrEnrgyRtCsRprt7-9-2026.pdf

BlackRock Section 19 notice, October 30, 2026 (all trusts): https://www.blackrock.com/us/individual/literature/tax-information/section-19-october-30-2026.pdf

UTF Section 19 notice, October 27, 2026: https://www.prnewswire.com/news-releases/cohen--steers-infrastructure-fund-inc-utf-notification-of-sources-of-distribution-under-section-19a-302921324.html

UTF rights offering terms and result, 2025: https://www.sec.gov/Archives/edgar/data/1275617/000119312525200137/d938187d497ad.htm and https://www.sec.gov/Archives/edgar/data/1275617/000119312525242018/d937837d497ad.htm

CII at-the-market supplement, July 27, 2026: https://www.sec.gov/Archives/edgar/data/1278895/000119312526318206/d98374d424b2.htm

BST at-the-market supplement, May 29, 2026: https://www.sec.gov/Archives/edgar/data/1616678/000119312526248381/d81899d424b5.htm

Cboe delayed option quotes for IEF: https://cdn-api.cboe.com/api/global/delayed_quotes/options/IEF.json

XLU distribution yield 2.77%, XLI 1.11% (State Street fund pages, Nov 12 2026): https://www.ssga.com/us/en/intermediary/etfs/state-street-utilities-select-sector-spdr-etf-xlu and https://www.ssga.com/us/en/intermediary/etfs/state-street-industrial-select-sector-spdr-etf-xli

AMLP trailing twelve-month yield 8.10% and expenses 1.01% (ALPS, Nov 13 2026): https://www.alpsfunds.com/exchange-traded-funds/amlp

## Things to be careful with

The Section 19 source splits are estimates. BlackRock revises them as the year goes on and the real tax character only shows up on the 1099. August is the obvious case, the 31% return of capital in that notice later disappeared from the year to date total.

The post-June unrealized gain is my estimate. I take the June 30 figure, subtract what was paid out and add the NAV total return since. It ignores gains realized at a different cost basis and new money from the shelf, so treat it as a rough number. The December annual report will have the real one.

The three return cases come from one decade of BUI's own history. That decade had a utilities boom, 2022 and a rate hike this September, but it's still only ten years.

The target uses the median premium since 2016. Since 2023 the median has been slightly negative (-0.26%), which would take about 20 cents off the target.

The June book replay assumes the June 30 holdings were held unchanged to November 13 and ignores dividends. The fund trades, and SpaceX had left the top 10 by October 30, so treat it as a map of where the pressure came from.

The rate sensitivity is a simple weekly regression. It moves a lot from year to year (positive in 2025, strongly negative in 2026), so it says what has been driving the NAV, not what will.

The margin path assumes about four and a half monthly payments between mid-November and March 31 and no special distribution, which would lower NAV and raise the payout rate on NAV.

The listed holdings file uses SOLV Energy's real ticker, MWH. An earlier version of my replay pulled SOLV, which is a different company (Solventum). National Grid is priced through its US ADR.

The rights offering list comes from EDGAR full-text search and may miss some.

The event study is simple averages, not a model. BlackRock's discount program (January to September 2026) and the broad CEF selloff in October 2026 both sit inside it.

The Monte Carlo resamples one decade of BUI's own returns. It is a way to size the odds, not a forecast.

The duration estimate comes from one year of weekly data and its band is wide. The rolling beta has faded since the first half of 2026. The 10-year explains only about 21% of BUI's weekly NAV variance in 2026, so a rate hedge removes some risk, not most of it.

The rates-flat return uses a 7% sector EPS growth figure from Gabelli's June 26, 2026 utility outlook ("consensus EPS CAGR expectations exceeding 7%"). The earnings-yield comparison in the post uses Gabelli's "approximately 18x 2027 EPS" adjusted by XLU's price change since June 30.

The switch backtest has 12 episodes, overlapping signal days and one huge episode (March 2020, +38.8 points). It is not significant at 5%. My Nasdaq rebuild of UTF's Section 19 gap gives -0.64 at September 30 against -0.57 in Cohen & Steers' own notice, and about +0.62 at October 30 as old months roll off. I quote their number for September 30. UTF's 28% leverage adds risk in an equity selloff.

The discount model explains about a third of the cross-section (R-squared 0.34) and uses CEF Connect's fields as published.

The NAV rebuild holds the foreign quarter of the book and cash flat, and assumes the June 30 positions were unchanged. Foreign holdings are Level 2 (fair-valued) in the N-PORT.

The implied volatility comes from IEF options, not MOVE or swaptions, which I couldn't pull from a free source. IEF tracks 7 to 10 year Treasuries, so I scale by IEF's own measured sensitivity to the 10-year.

The spread estimate is from daily highs and lows. Check the live quote.

peers_relative_value.py and rate_beta_tests.py run the same model (10-year, RSP, SMH, USO), but peers_relative_value.py stops at November 6 and rate_beta_tests.py now includes the week to November 13. The post and the vehicle table use rate_beta_tests.py. That one week moves the 2026 betas a lot (BUI -10.5 to -6.2), so treat any single 2026 rate beta as rough; the target uses 8, with 6 and 10.5 either side.

Shares outstanding after June 30 are two points only (June 30 report, November 13 product page). There is no daily issuance series, so issuance is tested by period, not by day.

The own-history discount model is a loose fit (R-squared 0.22 for BUI, 0.05 for UTF), so I don't lean on UTF's residual.

The ETF replication uses ETFs that hold different things from BUI (IGF is global infrastructure, IEF is Treasuries). None of the alphas is significant at 5%.

FedWatch odds in the post come from press reports of CME data (Investing.com, November 10; The Motley Fool, November 16), not from CME's page directly.

The book-like style set uses price returns for XLU, AMLP and XLI and takes off weight x today's trailing yield. Yields moved over the decade, so that adjustment is approximate. The 53-week results since BUI dropped calls are fitted on the same weeks they're measured on.

I've run about two dozen tests on this fund. One or two could clear 5% by chance. The post leans only on results that hold across methods.

CEF Connect showed BUI at -0.33% on Nov 13 against -0.64% on BlackRock's own $26.38 NAV. I use BlackRock and Nasdaq.

Things to be careful with in the newer scripts: the attribution is price only and uses quarter-end books, so it can't see trading between them; the bucket ETFs are rough stand-ins (IGF for rail and airports most of all); after June 30 only the US-listed names have prices until September's N-PORT. The payout triggers come from BlackRock's behaviour, not a stated rule. The CEF screen charges leveraged funds their borrowing costs without crediting the extra return, and gives every sector fund a 0.08% sector ETF.

## Corrections

16 Nov 2026: duration_and_valuation.py and position_pnl.py charged the hedge the full 10-year yield (5.15%). A short Treasury position also earns roughly the bill rate on its proceeds, so the hedge costs the 10-year yield minus the 3-month bill rate (about 0.86 points). The hedged position earns about 7.8% a year before premium changes, not 3.4%. The old 3.4% was close to the hedged return in excess of bills, but it was labelled as the return itself. Both scripts are fixed.

16 Nov 2026: tax_character.py said about 70% of 2026's payout would be taxed at ordinary rates. That counted all net income as ordinary. BUI designated 85% of its 2025 ordinary dividends as qualified, so the estimate is about 44% if 2026 is similar. Fixed, and after_tax_yield.py added.

18 Nov 2026: the article compared BUI's annual tax bill with XLU's (about 1.5 points a year in the top bracket) as if it were a cost like a fee. It isn't all cost, because an XLU holder pays tax on the gains later, when they sell. after_tax_wealth.py measures the real cost on after-tax wealth at the end of the hold: about 0.7 points a year over five years on this year's mix. The new-money threshold for a top-bracket taxable account moves from about 10% to about 8% for a five-year hold.

18 Nov 2026: vehicle_table.py mixed bases for costs (UTF before leverage, DNP with it) and had GLU at 1.35%. All four funds are now shown before and with leverage costs from their latest reports; GLU is 1.13% annualised in its June 30, 2026 semi-annual report and DNP 0.95% before leverage.

18 Nov 2026 (later): attribution.py no longer includes 14 Nov to 31 Dec 2025. Its start weights were backed out of the December book on the assumption that BUI didn't trade, during the weeks it was rebuilding the whole book. The window is now 31 Dec 2025 to 13 Nov 2026, and the totals changed accordingly (holdings +9.6% against +8.1%, sector bets -1.1, stock picks +3.4). Prices and NAVs used for the target, the ladder, the payout model and the CEF screen are refreshed to the November 17 close; the screen now uses CEF Connect's final history instead of a live snapshot.

18 Nov 2026 (later still): the post said the manager made money trading between quarter-ends, on the strength of the per-share gains line in the financial highlights. That line is partly a balancing figure, and 2.4m shares were issued in the same half. nav_gap.py now checks it in dollars as well. The gap survives ($14.7m), but the post now says it is consistent with trading gains rather than that it proves them.

19 Nov 2026: prices, NAVs, yields, the Treasury curve and the borrow fee are refreshed to the November 18 close. Adding the week to November 13 to the rate regressions moved BUI's 2026 rate beta from -10.5 (t -3.5) to -6.2 (t -1.7) and XLU's from -15.3 to -9.2. The post had said BUI's rate beta was about where it was in 2020; it now says the estimate is shaky and uses 8 as the middle case, which is what the target always used. The CEF screen moves to 32 funds passing both tests and 31 failing both.

19 Nov 2026: two wording fixes in the post. It said the unexplained NAV return turned negative from July; nav_gap.py has Q3 at +0.3 and Q4 to November 13 at -1.8, so it now says from October. It said BUI's premium melted right after the rights offering was announced; it actually rose to 10.3% on March 5 and fell once the shares went ex-rights on March 9, which the post now says.

