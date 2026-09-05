# Cena Certa — canonical production batches

This directory is the only accepted ingress for production batch JSON files.

Rules:
- exactly 10 candidates per batch;
- admission only through `../batch_admit.py`;
- every candidate must pass the certified Factory V2 preflight, including rights, relevance, anti-repeat, source-cleanliness, semantic scene plan, music and schedule gates;
- batch files are immutable after admission;
- admitting a batch does **not** enable production;
- `dispatch.json` remains the single execution gate;
- scheduling/publication remains blocked until the exact human approval gate is opened;
- no Base64 media route, blind retry, dead route or alternate publisher route is allowed.
