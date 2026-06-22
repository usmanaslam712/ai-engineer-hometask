# PayWallet Support Bot

A command-line support bot that answers PayWallet customer questions. It routes each question into one of four lanes — **ANSWER**, **REFUSE**, **ESCALATE**, or **OUT_OF_SCOPE** and replies based only on approved policy and the customer's own account data.

---

## Requirements

- Python 3.10 or higher
- No external packages needed except for running tests

Check your Python version:
```bash
python3 --version
```

---

## Setup

**1. Clone the repo and navigate into it**

```bash
git clone https://github.com/YOUR_USERNAME/ai-engineer-hometask.git
cd ai-engineer-hometask
```

If you already downloaded it manually instead of cloning:
```bash
cd /path/to/ai-engineer-hometask
```

Not sure where it is? Run this to find it:
```bash
find ~ -type d -name "ai-engineer-hometask" 2>/dev/null
```

**2. Install pytest (only needed for tests)**

```bash
pip3 install pytest
```

That's it. No other dependencies.

---

## Ask a question

Replace `CUSTOMER_ID` with one of `cust_001`, `cust_002`, or `cust_003`.
Replace `YOUR QUESTION HERE` with any question.

```bash
python3 bot.py --customer CUSTOMER_ID --question "YOUR QUESTION HERE"
```

**Examples to copy and paste:**

```bash
# Ask about freezing a card
python3 bot.py --customer cust_001 --question "how do I freeze my card?"
```

```bash
# Ask about balance
python3 bot.py --customer cust_001 --question "what's my balance?"
```

```bash
# Try a duplicate charge
python3 bot.py --customer cust_002 --question "I was charged twice for Netflix, what's going on?"
```

```bash
# Try asking for restricted data
python3 bot.py --customer cust_001 --question "can you tell me my full card number and CNIC?"
```

```bash
# Try an off-topic question
python3 bot.py --customer cust_001 --question "what's the weather like today?"
```

```bash
# Try in Urdu
python3 bot.py --customer cust_002 --question "mera card freeze kaise karun?"
```

---

## Run all 9 test questions at once

```bash
python3 bot.py --all
```

This runs every question in `materials/questions.txt` and prints the lane, topic, and reply for each one.

---

## Available customers

| Customer ID | Name | Account Status |
|-------------|------|----------------|
| cust_001 | Ayesha | Active |
| cust_002 | Hamza | Active (card frozen) |
| cust_003 | Sana | Restricted (KYC pending) |

---

## What the bot will return

Each reply shows:
- **Lane** — what kind of response this is
- **Topic** — the specific issue detected
- **Reply** — the message the customer would receive

| Lane | Means |
|------|-------|
| ANSWER | Bot answered from approved policy or account data |
| REFUSE | Request was for sensitive data (card number, CNIC, etc.) |
| ESCALATE | Issue needs a human agent |
| OUT_OF_SCOPE | Question is unrelated to PayWallet or is spam |

---

## Run the tests

```bash
python3 -m pytest tests/ -v
```

Expected output: **28 passed**

---

## Project files

```
bot.py          Main program
customer.py     Loads customer data (sensitive fields are never exposed)
router.py       Decides which lane a question goes into
llm.py          Generates the reply (swap in a real AI model here)
tests/
  test_bot.py   28 automated tests
materials/
  knowledge.md      Approved policy the bot can use
  customers.json    Mock customer data
  questions.txt     The 9 test questions
part-2-design/
  DATA_LAYER_DESIGN.md    Scalable governed data layer design (Part 2)
  diagram-logical.png     Logical architecture diagram
  diagram-technical.png   Technical layers diagram
DECISIONS.md    Every design decision explained with alternatives and reasoning
TESTING.md      Full test record — automated tests and manual terminal runs
README.md       This file
```

---

## What else is in this repo

**`DECISIONS.md`** — the main design document. Covers every meaningful decision made: why four lanes, how grounding works, why restricted fields are excluded structurally, how each of the 9 questions was routed and why, the guardrails added, and what was deliberately left out. Written to be walked through live.

**`TESTING.md`** — records all testing done: the 28 automated pytest cases with what each one proves, and the manual terminal tests run against the guardrails (weather, political questions, Urdu food question).

**`part-2-design/`** — the Part 2 design note. Covers how the bot should fetch live customer data from multiple owning services through a single governed gateway, with positions on data ownership, field-level access control, handling slow or down services, data residency, adding new data signals, and scaling. Includes two architecture diagrams.
