# LSI Capital Learning Policy R1

## Objective
Improve capital-allocation decisions over time while keeping simulated and real-money states strictly separate.

## Daily learning dimensions
For every PAPER position/decision store: thesis, source evidence, expected return range, downside case, catalyst, invalidation condition, valuation/macro regime, position size, realized/unrealized P&L, drawdown, opportunity-cost benchmark, decision latency, and post-mortem lesson.

## Promotion logic
A strategy is not promoted because a book, investor or model recommends it. Promotion requires repeated out-of-sample evidence across market regimes, acceptable drawdown, positive excess return versus the relevant benchmark after costs, and no truth/safety violations.

## Failure taxonomy
- THESIS_WRONG
- VALUATION_TOO_HIGH
- TIMING_NOISE
- MACRO_REGIME_SHIFT
- EARNINGS_DETERIORATION
- BALANCE_SHEET_RISK
- MANAGEMENT_CAPITAL_ALLOCATION
- POSITION_TOO_LARGE
- SOURCE_STALE_OR_WRONG
- BENCHMARK_OPPORTUNITY_COST
- EXECUTION_COST
- MODEL_OVERCONFIDENCE

## Real-money firewall
The learning engine may autonomously research, rank, simulate and draft orders. It may not submit, modify or cancel a real order without the authorization required by the connected execution mechanism. No broker credential, private key or account secret may be copied into public repositories or learning logs.

## Growth objective
The operational objective is rising long-run capital with controlled risk, not an impossible guarantee that every day is positive. Daily losses are valid learning data and may be preferable to hidden tail risk. The engine optimizes risk-adjusted compounded return and survival, with cash/opportunity cost explicit.
