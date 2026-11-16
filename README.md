# bui-payout-margin

This is the data and code behind my Seeking Alpha piece on BlackRock Utilities, Infrastructure & Power Opportunities Trust (BUI), November 2026: "BUI: Fair At NAV, And Rates Hit It Twice", and my X thread on utilities losing their stock-market beta in 2026.

The short version: in 2026 utilities lost their link to the stock market and kept their rate risk. BUI's NAV has about 8 years of effective rate duration this year (range 6 to 10.5), close to a 10-year Treasury note, while it pays 7.01% of NAV from a book yielding about 2.8%. The target is built from 10-year scenarios. The Section 19 coverage number has a weak spot at December 31, 2026 and then gets lifted by base effects through 2027.

Plain Python 3. The newer scripts and rate_beta_tests.py need numpy, pandas and statsmodels (pip install numpy pandas statsmodels). The older ones run on the standard library.

## How to run it

From anywhere:

    python scripts/payout_hurdle.py

Each script reads from data/ relative to itself and prints to the screen. My own output is saved in results/.

## What each script does

scripts/issuance_test.py checks whether BlackRock actually sells BUI shares into the premium and whether that caps it. Shares outstanding rose 496,220 (1.87%) from June 30 to November 13; the shelf sold 1,373,141 shares in 2025 and none in the first half of 2026. 2025 sold at about the same monthly pace as since July and the premium still averaged about 2%, so selling trims the premium rather than capping it.

scripts/discount_own_history.py compares BUI's discount with its own history since 2017 (monthly, on its distribution rate, the 10-year and its trailing NAV return). Today's discount is within 0.6 points of fitted. Each 1-point rise in the 10-year has come with about a 1.1-point wider discount (t -3.1).

scripts/switch_backtest.py is the UTF switch test. It flags every day since November 2016 when UTF's discount minus BUI's was 5 or more points below its own trailing one-year median and measures UTF minus BUI total return over the next 12 months (12 episodes, UTF won 9, average +9.6 points; all signal days 73% hit rate and +5.6 points against 57% and -0.7 on all days; block bootstrap about 0.11). It also fits weekly half-lives for each discount and the spread (BUI about 4 weeks, UTF and the spread about 7 to 8), the mid-November to year-end and January seasonality, and BUI's premium before and since the July 1 at-the-market supplement.

scripts/premium_lid.py compares premiums before and after the 2026 at-the-market supplements for BUI, CII and BST, against 20 control funds. issuance_test.py supersedes its conclusion: the premium fell after July, but the issuance data say selling isn't what capped it.

scripts/nav_rebuild.py rebuilds BUI's NAV daily from the June 30 N-PORT for the 32 listed names (74.7% of net assets, R-squared 0.92 against the reported NAV, -2.18% against -2.83% reported from June 30 to November 13) and checks daily against weekly rate betas for BUI's NAV, XLU and SPY.

scripts/discount_screen.py regresses the discount of 108 equity CEFs on distribution rate, NAV return, leverage, size and expenses, and ranks the utility and energy-infrastructure funds by what the model doesn't explain (BUI +9.8 points rich, UTF +1.8).

scripts/section19_platform.py ranks BUI's Section 19 gap among BlackRock's equity trusts, puts UTF's own notice next to it (-0.57), and shows how often the final tax character included return of capital, 2023 to 2025.

scripts/implied_rate_vol.py turns one-year IEF option implied volatility into a 10-year yield volatility (about 1.06 points) and reruns the scenario target with it ($26.38, unchanged).

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

scripts/duration_and_valuation.py turns the betas into an effective duration (central 8, range 6 to 10.5), compares it with the 10-year note (7.74 at 5.15%), gives the hedge ratio (about $103 of 10-year notes per $100 of BUI), the hedged volatility and carry, and the $26.38 target from 10-year scenarios.

scripts/target.py is the older history-based target ($27.09). I keep it as a cross-check.

scripts/regime_shift.py regresses weekly and daily returns on the 10-year yield change and the S&P 500 together, year by year, for XLU and BUI's NAV. In 2026 XLU's S&P beta is about zero (-0.23 weekly) and its weekly correlation with SPY -0.10, against +0.57 in 2025. BUI's NAV loses about 8.7% per +100bp, its most since 2017.

scripts/section19_base_effects.py runs the Section 19 margin forward to December 2027 at flat, 5% and 8.28% NAV returns, shows which 2021-2022 months leave the 5-year window, finds the NAV move that turns the December 31, 2026 margin negative (about -3%, or -2.5% with a $0.50 special) and how often BUI has fallen that much in 32 trading days.

scripts/payout_simulation.py resamples 12-month blocks of BUI's monthly NAV returns three years forward at the current payout: about a 36% chance the margin goes negative at some month-end by December 2027.

scripts/discount_event_study.py compares discounts before BlackRock announced the end of call writing and now, for the seven funds that dropped it, the four BlackRock funds that kept options, and 97 other equity CEFs.

scripts/ipo_sleeve.py covers the three 2026 IPO names in the June book (SpaceX, Fervo Energy, SOLV Energy): IPO price, June 30 and November 13 values, about -$0.25 a BUI share if still held.

scripts/blackrock_platform.py puts BUI next to the rest of BlackRock's CEF platform: seven rights offerings since June 2025 (about $1.0bn raised), SpaceX at 3.0-3.1% of net assets in four BlackRock CEFs, what the seven funds that dropped call writing did with their payouts, and how fast the rights offering fee pays back BlackRock's costs (about 5.5 months).

scripts/payout_hurdle.py gives the 7.01% hurdle, the 2,262 rolling 12-month NAV return windows since November 2016, the 61% of them that cleared the hurdle, the 17.1% that were negative, the histogram buckets, and the 10-year and 5-year annualized NAV return.

scripts/section19_margin.py gives the month by month gap (and flags the $0.104 a share drop in year to date short-term gains between the September and October notices) between the 5-year NAV return and the distribution rate, straight from the notices, plus the fiscal year to date payout mix (30% income, 40% short-term gains, 30% long-term gains).

scripts/nii_coverage.py gives net income against distributions from 2021 to the first half of 2026, the 25% coverage figure, and the $1.88 a share of return of capital paid from 2021 to 2024.

scripts/precedent.py replays 2021 to 2024 (5.25% a year NAV return, NAV down 4.8%) and runs the same four years from today's NAV at today's payout ($24.37).

scripts/gains_reservoir.py gives the $7.89 a share of unrealized gain at June 30 and my estimate of about $6.34 now.

scripts/since_raise.py gives NAV, price and XLU since June 30, and the August and September month-end NAV.

scripts/premium.py gives the premium/discount history (median +0.56%, the 2026 high of +10.28% on March 5, and the latest -0.64%).

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

peers_relative_value.py and rate_beta_tests.py run the same model (10-year, RSP, SMH, USO) but build weeks slightly differently, so UTF's 2026 rate beta comes out -10.1 in one and -9.8 in the other. The post uses -9.8 from rate_beta_tests.py.

Shares outstanding after June 30 are two points only (June 30 report, November 13 product page). There is no daily issuance series, so issuance is tested by period, not by day.

The own-history discount model is a loose fit (R-squared 0.22 for BUI, 0.05 for UTF), so I don't lean on UTF's residual.

## Corrections

None so far.
