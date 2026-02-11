# Decision Log

Record of significant decisions made during the project.

When you make a decision that affects the project direction, add it here so we remember why.

---

## Template

Copy this for new decisions:

```
### [DECISION-XXX] Short Title

**Date:** YYYY-MM-DD  
**Decided by:** Name(s)  
**Status:** Accepted / Superseded by DECISION-XXX

**Context:**
What situation prompted this decision?

**Options Considered:**
1. Option A - pros/cons
2. Option B - pros/cons
3. Option C - pros/cons

**Decision:**
What we chose and why.

**Consequences:**
What this means for the project going forward.

---
```

---

## Decisions

### [DECISION-001] Target Variable Encoding

**Date:** [TBD]  
**Decided by:** Team  
**Status:** Pending

**Context:**
The crash data has injury severity as text. We need to encode it for ML.

**Options Considered:**
1. Binary (injury vs no injury) - simpler, but loses information
2. 3-class (none, minor/moderate, severe/fatal) - balanced classes
3. 5-class (none, minor, moderate, severe, fatal) - full granularity but imbalanced

**Decision:**
[TBD - discuss in first meeting]

**Consequences:**
- Affects model choice (binary classifier vs multi-class)
- Affects evaluation metrics
- Affects class imbalance handling

---

### [DECISION-002] Train/Test Split Strategy

**Date:** [TBD]  
**Decided by:** Team  
**Status:** Pending

**Context:**
Need to split data for model evaluation.

**Options Considered:**
1. Random 80/20 split - simple but might have temporal leakage
2. Temporal split (train on older, test on newer) - realistic but might miss patterns
3. Stratified random split - preserves class distribution

**Decision:**
[TBD]

**Consequences:**
- Affects how we report model performance
- Affects whether results generalize to future data

---

### [DECISION-003] Webapp Framework

**Date:** [TBD]  
**Decided by:** Team  
**Status:** Pending

**Context:**
Need to choose a framework for the interactive webapp.

**Options Considered:**
1. Streamlit - easy to build, Python-only, good for data apps
2. Flask + vanilla JS - more control, more work
3. Dash - Plotly-based, good for dashboards

**Decision:**
[TBD]

**Consequences:**
- Affects development time
- Affects what visualizations are easy/hard
- Affects deployment options

---

*Add new decisions above this line*
