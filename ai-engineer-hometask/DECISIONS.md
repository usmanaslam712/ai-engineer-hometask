# DECISIONS.md — Part 1

---

## What this contains
- The assumptions I had before proceeding to the decision making to each question and scenario.

- How decision making is done via the four lanes I chose.

- How each question was tackled according to what was present in `knowledge.md` and what could be gathered or utilized from `customers.json`.

- How and why the bot took the mentioned decision, any alternative method, my reason behind choosing the current decision or action, anywhere Im rather unsure.

- Any existing limitations and their reasoning.

- Guardrails to prevent the bot from replying to messages that would be considered out of context or shouldnt be answered. How Guardrails overall work in the bot.

- Whats not included and their reasoning.

---

## Assumptions (pre-decisions)
Before arriving to the decision process for what the bot should do, it's assumed that:

- The customer has already authenticated and logged into the app, hence the `customerId` has already passed.

- The safe and restricted split in the `customers.json` file is correct and doesn't require any re-judging.

- The bot currently reads data and answers accordingly but doesn't make any changes.

- The app has some parallel features to regular banks but doesn't invent any on its own.

---

## 1. Decision process via four lanes (ANSWER / REFUSE / OUT_OF_SCOPE / ESCALATE)
*Applies to all 9 questions*

**Decision:** Every question is classified into exactly one of four lanes of decision before a reply is generated.

- **ANSWER** - The bot answers the query accordingly based on information present in `knoweldge.md` or the safe block within `customers.json`

- **REFUSE** - The bot refuses to take action on something it isnt allowed to do based on anything that may seem confidential or in the restricted block of `customers.json`.

- **OUT_OF_SCOPE** - The bot does not answer or share any information that isn't aligned with the policies mentioned in `knowledge.md`. This also includes responding to questions that are not related to the product or any message that may seem spam.

- **ESCALATE** - The bot identifies a problem but can not take full action hence it pushes to the Customer Success team to resolve it

**Alternatives considered:**
- Binary decision lane i.e. answer/don't-answer: Binary decision function is too limited and would not be able to serve different customer approached.

- Free-form routing decided by the LLM: Could be unpredictable if model decides freely for the current test.

**Why I chose this:** In every question, there are possible four different situations that come up ranging from what can be answered to a problem that a human can better handle. Particular questions related to crypto and savings interest flag a need for escalation or out of scope.

**What I'm unsure about:** The boundary between OUT_OF_SCOPE and ESCALATE is a tedious call. I have further documented the specific cases I resolved below per question.

---

## 2. Answers must trace to knowledge.md or safe customer data via customers.json
*Applies to all 9 questions*

**Decision:** A reply is valid only if it traces to one of two sources that is the policies within `knowledge.md` or the customer's safe fields within `customers.json`. Anything that isnt present in either of the files or has ambiguity is refused or escalated to human.

**Alternatives:**
- LLM general knowledge as a third source was immediately ruled out as the bot would invent fees, timelines, and steps that aren't policy unless the bot was further trained to take on newer instructions or commands.

**Why I chose this:** The bot would need both sources as `knowledge.md` alone can't answer questions like "what's my balance?" as that's in the customer record and customer experience would need to be top notch The customer record via `customers.json` alone can't explain how to freeze a card without verifying from the policies file. Both files cover different things and don't overlap, so using both doesn't create ambiguity about where an answer came from.

---

## 3. The bot can state a safe fact but can't invent the policy around it
*Based on questions 5 and 7, applies anywhere safe data and a missing policy meet*

**Decision:** The bot is allowed to tell the customer what the data shows based on their customerId and the safe block. It is not allowed to explain the why, the how to fix it, or the outcome because those would need a policy, and the policy has to be in `knowledge.md`. Any explanation would be handled by Customer Support team.

**Why this matters:** "Your verification is pending" is in the data, so the bot can say it however "That's why your account is restricted" is not in the data which meansd that would be me adding a reason that isn't in `knowledge.md` hence inventing a new policy.

---

## 4. Restricted fields never enter the answer path
*Question: `cust_001 | can you tell me my full card number and CNIC?`*

**Decision:** CNIC, PAN, and IBAN are never loaded into the answer path as `customer.py` returns only the `safe` block; the `restricted` block is never read.

**Alternatives considered:**
- Load everything but filter on output. In this method, the restricted values would exist in memory and in any prompt sent to the bot LLM but a creative question or a prompt-injection attack could still surface them hence this was ruled out.

**Why I chose this:** If the values were never loaded, they can never leak. With output filtering the values would still be in memory and a creative question or prompt injection could still get them out. Simply not loading them at all removes the entire risk. The tests check that no restricted value appears in any reply which is an existing safety procedure but not an overall guaranteed method.

**What I'm unsure about:** When the bot escalates a case to a human, the agent would need more context to help the correct customer. Atm I haven't built a handoff for this bot but plan is to pass customer ID and contenxt and not the restricted data. The Customer Success person would have to utilize internal tools to pull sensitive data.

---

## 5. Crypto = OUT_OF_SCOPE, savings rate = ESCALATE
*Questions: `cust_001 | do you offer crypto trading?` and `cust_001 | what's the interest rate on the savings account?`*

**Decision:** Crypto trading routes are considered OUT_OF_SCOPE while a question about the savings account interest rate routes to ESCALATE.

**Alternatives considered:** Treating both as ESCALATE, or both as OUT_OF_SCOPE. Crypto could arguably be an ESCALATE if the feature would be something PayWallet would be aiming to support.

**Why I chose this:** For the Crypto related query, PayWallet doesn't support or offer crypto so by default it comes within the OUT_OF_SCOPE lane. However, in the interest rate question, this may be considered as general banking information which a Customer Support individual could better answer and explain.

**What I'm unsure about:** If PayWallet genuinely has no savings account product, the savings-rate question should become OUT_OF_SCOPE too. I don't have enough context to be certain if this would be considered something in the future, so I defaulted this to ESCALATE as it's safer than saying no.

---

## 6. Duplicate Netflix charge = ESCALATE with no refund promise unless investigated by CS
*Question: `cust_002 | I was charged twice for Netflix, what's going on?`*

**Decision:** Q3 (Hamza charged twice for Netflix) escalates to Customer Support. The reply acknowledges the visible duplicate from safe data but makes no promise about a refund or outcome.

**Alternatives considered:** Answering with the refund-timeline section as part of `knowledge.md` that section covers how long a refund takes once a merchant processes it. However, it says nothing about whether a refund will be issued or not based on the situation. Mentioning it here would imply a refund is coming, which is something a bot couldn't promise on.

**Why I chose this:** The transaction record mentions the duplicate record so acknowledging the situation is fine for the bot. However, the `knowledge.md` has no dispute or chargeback policy, so I can't say what happens next.

---

## 7. Sana account restricted = ESCALATE
*Question: `cust_003 | why can't I do anything on my account?`*

**Decision:** Sana's question escalates to Customer Support. The bot can simply see her account state in the safe data and acknowledge her concern, but it can't resolve the restriction itself. Looking at this from the customer's side, she wants the problem fixed, not just to hear the WHY So the bot states what it can see and hands the rest to a Customer Support representative.

**Why this escalates:** Sana asked for the WHY and the FIX and this is exactly the things the bot cannot manufacture or resolve on its own. There is no KYC or account-restriction policy in `knowledge.md`, so the bot has no approved answer for either. Customer Support could primarily state the reason and how to resolve the problem,

**Different variations I went through:**
To conclude with the final answer, I worked around with different variations while keeping in mind of the customer's POV.

**(a) Mention the actual reason:** "Your KYC is pending, that's why your account is restricted.", this version of the response was rejected. As there is no account restriction policy in `knowledge.md` and mentioning it might lead to inventing a policy.

**(b) State the safe fact** — Initially chosen, but the draft led with the bare acronym "KYC" and such jargons are not commonly understood by the causal consumer which would lead to confusion and ambiguity and bad customer experience.

**(c) Surface the safe fact in plain language** — This was the final variation. "Your account isn't fully active yet. Verification is still pending." which translates the safe field into something the customer can actually understand. This avoids any confusion or bad experience and would later allow the customer to redirected to Customer Support.

**What I'm unsure about:** Guiding the user directly on how to resolve this but then it would be an invention of a new polciy. Responding vaguely would also lead to bad customer experience. For this, I aimed at reasoning in plain language with direct escalation for smoother customer experience and support which would also lead to record customer feedback and add improvements.

---

## 8. Urdu question routes like English
*Question: `cust_002 | mera card freeze kaise karun?`*

**Decision:** "mera card freeze kaise karun?" routes the ANSWER to the English equivalent.

**Why it works here:** The question contains "card" and "freeze"  which is commonly used in Pakistani Urdu when speaking about banking apps. The keyword router matches on these.

**Limitation:** There is no Urdu support atm. It works for this specific question because those two words happen to be borrowed from English. A question written in full Urdu script would match nothing and by default would fall through to OUT_OF_SCOPE. A real multilingual bot would need transliteration handling or a language-detection and translation step before routing.

---

## 9. Guardrails block off-topic and spam before any support logic runs
*Applies to any input*

**Decision:** Two guardrails sit at the top of the router, before REFUSE and before any support logic. Off-topic questions (weather, news, jokes, sports, stock prices) route to `OUT_OF_SCOPE / off_topic`. Spam inputs and out of context questions route to `OUT_OF_SCOPE / spam`.

`REFUSE` however is not a routing decision though but rather a hard block.

**What the guardrails prevent:**
- **Off-topic** — stops the bot from being used as a general-purpose assistant. Without this, a question like "what's the weather in Karachi?" would fall through to `OUT_OF_SCOPE / no_match` anyway, but the guardrail makes the intent explicit and allows a more specific reply like "I can only help with PayWallet account questions"  rather than a generic deflection.

- **Spam** — stops the bot wasting a reply cycle on gibberish or repeated characters. Also prevents edge cases where a string of symbols might accidentally keyword-match something in the router.

**Why OUT_OF_SCOPE is being used:** Both are cases where no human is needed and no PayWallet policy is relevant. Hence no need to add a new lane, OUT_OF_SCOPE works well in this case. Adding a new lane would result in more complexity, however REFUSE is not a lane but simply a block.

---

## 10. Retrieval is keyword/section matching
*Applies to all 9 questions*

**Decision:** The router matches questions to knowledge.md sections and lanes using keywords. This version of the bot does not use any form of semantic search.

**Why I chose this:** knowledge.md has only six sections to test the lanes accordingly. Keyword matching is simple to test it agaainst the decision lanes. Embeddings or adding AI powered semantic search would add complexity which isnt the current scope.

**Possible risks:** If an in-scope question is written differently, like instead of "freeze" it's "my card stopped working", then that would lead to a resulting lane decision of OUT_OF_SCOPE which would be false negative.

**If the scope grew:** Add synonym handling and different variations of the similar questions backed by an LLM.

---

## What I didnt include

- **Web UI:**  This wasnt asked for.

- **Semantic search:** knowledge.md has six sections and the questions map cleanly to them. Semantic search would add complexity and a dependency without improving correctness here.

- **Real LLM:** The stubLLM produces deterministic, testable output and forces every grounding decision to be explicit. A real model would hide those decisions inside the prompt, making them harder to defend in a live review. The `LLMBackend` protocol makes the swap one line of code when needed.
