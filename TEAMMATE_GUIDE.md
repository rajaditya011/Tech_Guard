# HomeGuardian AI — Teammate Guide

**For non-technical team members.** This guide explains everything about the project in plain English so you can present it confidently to judges.

---

## Table of Contents

1. [What Is HomeGuardian AI?](#1-what-is-homeguardian-ai)
2. [The Problem We Solve](#2-the-problem-we-solve)
3. [How It Works (Simple Version)](#3-how-it-works-simple-version)
4. [How It Works (Technical Version)](#4-how-it-works-technical-version)
5. [Feature: Legacy Device Integration (F01)](#5-legacy-device-integration)
6. [Feature: Behavioral Intelligence Engine (F02)](#6-behavioral-intelligence-engine)
7. [Feature: Real-Time Vision Analysis (F03)](#7-real-time-vision-analysis)
8. [Feature: Smart Clip Extraction (F05)](#8-smart-clip-extraction)
9. [Feature: AI Incident Narratives (F09)](#9-ai-incident-narratives)
10. [Feature: Prediction Engine (F11)](#10-prediction-engine-secret-weapon)
11. [What Makes Us Different](#11-what-makes-us-different)
12. [Demo Mode and Scenarios](#12-demo-mode-and-scenarios)
13. [Tech Stack Explained](#13-tech-stack-explained)
14. [Security in Plain Language](#14-security-in-plain-language)
15. [Judge Q&A — Anticipated Questions](#15-judge-qa)
16. [3-Minute Pitch Script](#16-3-minute-pitch-script)
17. [Demo Preparation Checklist](#17-demo-preparation-checklist)

---

## 1. What Is HomeGuardian AI?

**HomeGuardian AI turns your old, unused devices — old phones, webcams, CCTV cameras — into an intelligent security network that learns your home's daily routine and alerts you when something does not belong.**

Think of it as giving your home a memory and a brain. It remembers what "normal" looks like, and when something breaks the pattern, it tells you exactly what happened, why it is suspicious, and what you should do — all with a video clip and a plain-English explanation.

---

## 2. The Problem We Solve

Traditional home security cameras have three massive problems:

1. **False Alerts Everywhere.** Motion detection triggers on pets, shadows, curtains, and wind. Homeowners get so many false alerts that they start ignoring all of them — including real ones.

2. **Hours of Useless Footage.** When something does happen, you have to scrub through hours of recorded video to find the relevant 10 seconds. Most people give up.

3. **Wasted Hardware.** Millions of old smartphones, webcams, and CCTV cameras sit unused in drawers. Each one has a perfectly good camera and internet connection.

HomeGuardian AI solves all three:
- It learns what "normal" looks like in your home, so it only alerts when something genuinely unusual happens.
- It automatically captures a short clip of just the suspicious event — no scrubbing required.
- It turns your old devices into the sensor network, so you spend zero on new hardware.

---

## 3. How It Works (Simple Version)

**Step 1 — Plug In Your Old Devices**
Take an old phone, webcam, or camera. Open the HomeGuardian Old Device Portal in its browser. It enrolls automatically — one tap, done.

**Step 2 — The System Learns Your Home**
For the first 7-14 days, the system watches and learns. It memorizes when people move through rooms, which areas are active at which times, and what patterns are normal. Think of it as the system building a "heartbeat" of your home.

**Step 3 — Monitoring Begins**
After learning, the system compares everything it sees against the learned baseline. Normal activity is ignored. Unusual activity is flagged.

**Step 4 — Something Unusual Happens**
When the system detects behavior that does not match the baseline, it:
- Captures a short video clip (not hours — just the suspicious 10-20 seconds)
- Writes a plain-English explanation of what happened and why it is suspicious
- Assigns a risk score from 0 to 100
- Sends everything to your phone instantly

**Step 5 — You Respond**
On your primary device (phone or laptop), you see the alert with the clip, the explanation, and recommended actions. You can even send a voice message through the old device's speaker.

---

## 4. How It Works (Technical Version)

*Use this version with tech-savvy judges.*

1. **Sensor Nodes:** Old devices stream video frames via MQTT (IoT messaging protocol) to the central AI hub. No processing happens on the old device — it only streams.

2. **Behavioral Baseline:** The AI hub runs DBSCAN clustering on movement trajectories and builds per-zone, per-hour activity probability distributions over 7-14 days of passive observation. The full statistical profile is stored in SQLite.

3. **Real-Time Analysis:** Every incoming frame passes through YOLOv8 for human detection and classification. Movement vectors and zone transitions are computed in real time.

4. **Anomaly Detection:** An Isolation Forest model scores each event against the learned baseline. Multi-sensor fusion cross-correlates events across all sensor nodes for spatial consistency.

5. **Risk Scoring:** Dynamic risk scores are calculated using weighted factors: baseline deviation (40%), time-of-day risk (20%), zone sensitivity (20%), event duration (10%), multi-sensor confirmation (10%).

6. **Intelligence Response:** On anomaly confirmation, the Smart Clip Extraction Engine assembles pre-event frames from a ring buffer and post-event frames into an MP4. The Claude API generates a plain-English incident narrative. FCM delivers a push notification with clip thumbnail.

7. **Prediction Engine (Secret Weapon):** A scenario library of intrusion behavioral signatures (casing, entry probing, reconnaissance, intrusion) enables predictive alerting — the system can raise a warning during the casing phase, before an intrusion attempt begins.

---

## 5. Legacy Device Integration

**Analogy:** Imagine turning every old phone in your drawer into a security guard that never sleeps and never asks for a paycheck.

How it works:
- Any device with a camera and internet connection qualifies — old phones, webcams, USB cameras, CCTV systems.
- The device opens the Old Device Portal in its browser and enrolls with one tap.
- Once enrolled, it streams video to the AI hub and does nothing else (saving battery and CPU).
- The system monitors each device's health — battery, connection, last heartbeat.

Why it matters for judges: Zero hardware cost is a massive competitive advantage. Most smart home security products require buying proprietary cameras.

---

## 6. Behavioral Intelligence Engine

**Analogy:** Think of the system memorizing your home's daily heartbeat — when the kitchen is active, when the hallway has foot traffic, when the front door opens and closes. After two weeks, it knows the rhythm of your life.

How it works:
- For the first 7-14 days, the system passively observes without sending any alerts.
- It builds a statistical profile: "On weekday mornings, the kitchen sees activity from 7:00-8:30 AM. The living room is active from 6:00-10:00 PM. The hallway has foot traffic throughout the day but zero activity after midnight."
- Every future event is compared against this personalized profile.
- If someone moves through the living room at 2:43 AM and the baseline says that zone has zero activity at that hour, that event is immediately suspicious.

Why it matters for judges: This is not a generic motion detector. It is a personalized behavioral model unique to each home.

---

## 7. Real-Time Vision Analysis

**Analogy:** Every camera feed passes through a set of AI eyes that can distinguish between a person, a pet, a shadow, and the wind.

How it works:
- The AI hub processes every video frame using YOLO, a state-of-the-art object detection model.
- It detects humans specifically, not just "motion."
- It tracks where each detected person moves and which room zones they pass through.
- All processing happens on the AI hub, not on the old device.

---

## 8. Smart Clip Extraction

**Analogy:** Imagine a security camera that records nothing normally — but the moment something suspicious happens, it instantly assembles a perfect 15-second highlight reel centered on the event, as if it "remembered" the last 5 seconds and "watched" the next 10.

How it works:
- During normal activity, a ring buffer silently holds the last few seconds of frames (like a short-term memory).
- When an anomaly is confirmed, the system grabs those pre-event frames, continues recording for 10 more seconds, and stitches everything into a timestamped MP4 clip.
- Every clip includes metadata: which sensor detected it, which zone, what the anomaly score was, and what the AI classified it as.

Why it matters for judges: This is a key technical innovation. Traditional cameras record everything and make you search. We record nothing and capture only what matters.

---

## 9. AI Incident Narratives

**Analogy:** Instead of getting a vague "Motion Detected" notification, you get a message that reads like a professional security officer's report.

Example output:
> "At 2:43 AM, unusual movement was detected in the living room. This zone typically shows zero activity between midnight and 6 AM based on 14 days of baseline data. The detected movement trajectory does not match any household member's known pattern. The event persisted for 47 seconds across two sensor nodes, confirming it is not a false positive. Risk assessment: High. Recommended action: verify household members are safe and check the attached clip."

Why it matters for judges: Explainability is a huge selling point. Users trust a system that explains its reasoning.

---

## 10. Prediction Engine (Secret Weapon)

**Analogy:** Most break-ins follow a predictable pattern — the intruder cases the house first, tests doors and windows, then enters. Our system detects the casing phase and raises a warning BEFORE the intrusion happens.

How it works:
- The system has a library of intrusion behavioral signatures based on criminology research.
- Phase 1 (Casing): Slow movement along the perimeter, repeated passes, no entry attempt.
- Phase 2 (Entry Probing): Brief contact with doors and windows, testing for access.
- Phase 3 (Reconnaissance): Interior movement if entry succeeds.
- Phase 4 (Intrusion): Extended unfamiliar presence.
- As live events arrive, the system matches them against these phase signatures.
- When Phase 1 matches with high confidence, the system raises a prediction: "This behavior matches the casing phase of a potential intrusion. 73% confidence."

Why it matters for judges: We catch intrusions BEFORE they start. That is our headline feature.

---

## 11. What Makes Us Different

| Feature                        | Traditional CCTV             | HomeGuardian AI                        |
| ------------------------------ | ---------------------------- | -------------------------------------- |
| Detection method               | Generic motion detection     | Personalized behavioral baseline       |
| False alarm rate               | Very high                    | Very low (learns what is normal)       |
| Hardware cost                  | $200-$500+ per camera        | $0 (uses existing old devices)         |
| Video recording                | Records everything 24/7      | Records only anomaly clips             |
| Alert content                  | "Motion Detected"            | Full narrative + clip + risk score     |
| Predictive capability          | None                         | Detects casing phase before intrusion  |
| AI reasoning                   | None                         | Full reasoning chain for every alert   |
| Storage required               | Terabytes of footage         | Megabytes of targeted clips            |
| Multi-sensor intelligence      | Cameras work independently   | Cross-correlates all sensors in real time|
| Communication                  | One-way (view only)          | Two-way (send voice to old device)     |

---

## 12. Demo Mode and Scenarios

The system can run a full demo without any external services. Everything is simulated with realistic synthetic data.

| Scenario | Name                             | What Happens                                                                       | Duration |
| -------- | -------------------------------- | ---------------------------------------------------------------------------------- | -------- |
| A        | Normal Morning Routine           | System shows learned baseline in action. Kitchen and living room active. No alerts.| 60 sec   |
| B        | Late Night Anomaly               | 2:43 AM motion in living room. Risk escalates. Clip generated. Narrative written.  | 45 sec   |
| C        | Casing Simulation                | Repeated passes at front door. System flags suspicion. 73% casing match.           | 90 sec   |
| D        | Full Intrusion Prediction        | 4-phase simulation. System catches casing, predicts intrusion BEFORE it happens.   | 120 sec  |

**For judges:** Start with Scenario A (show the system is smart enough to ignore normal activity), then jump to Scenario D (show the prediction engine in action).

---

## 13. Tech Stack Explained

| Technology         | What It Does                                 | Why We Chose It                              | What a Judge Might Ask                         |
| ------------------ | -------------------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| Python / FastAPI   | Backend server and API                       | Fast, modern, async, excellent for ML        | "Why not Node.js?" — Python has superior ML ecosystem |
| React / Vite       | Frontend user interface                      | Component-based, fast build, rich ecosystem  | "Why not Next.js?" — SPA is simpler for this use case |
| MQTT (Mosquitto)   | Communication between devices and hub        | Standard IoT protocol, lightweight, reliable | "Why MQTT over REST?" — See Q&A below          |
| YOLOv8             | Object detection in video                    | State-of-the-art accuracy, fast inference    | "Does it run real-time?" — Yes, on modern hardware |
| Claude API         | AI narrative generation                      | Best reasoning quality, structured output    | "What if the API is down?" — We have fallback templates |
| SQLite             | Database                                     | Zero config, portable, fast for single-node  | "Does it scale?" — Yes, can migrate to PostgreSQL |
| TailwindCSS        | Styling                                      | Rapid UI development, consistent design      | "Why not plain CSS?" — Speed of development    |
| Docker             | Container deployment                         | Reproducible builds, easy deployment         | "Can it run without Docker?" — Yes, all services are standalone |

---

## 14. Security in Plain Language

- **All secret keys** (API keys, passwords) are stored in environment variables, never in code files.
- **Login tokens expire quickly** (15 minutes) and must be refreshed — so a stolen token becomes useless fast.
- **Every input is checked** before the system processes it — no one can inject malicious data.
- **Device communications are authenticated** — only enrolled devices can send data to the AI hub.
- **Error messages are generic** to users — attackers cannot learn about the system from error messages.
- **Video clips are access-controlled** — you need a valid token to view any clip.
- **Rate limiting prevents abuse** — you cannot spam the login page or flood the system with fake data.
- **All dependencies are version-locked** — we know exactly what code is running, no surprise updates.

---

## 15. Judge Q&A — Anticipated Questions

### Q1: How does the baseline learning actually work?

**Answer:** "For the first 7-14 days, the system passively observes all sensor input without generating any alerts. It builds a statistical profile for every zone in the home at every hour of every day. It tracks activity probability, movement speed distributions, and trajectory patterns using DBSCAN clustering. After the learning period, every new event is compared against this personalized baseline. If an event deviates significantly from what the system has learned is 'normal' for that zone and time, it is flagged as anomalous."

### Q2: What happens with false positives?

**Answer:** "False positives are dramatically reduced because we do not use generic motion detection. Our baseline is personalized to each home. Additionally, multi-sensor fusion cross-correlates events across multiple sensor nodes — a single motion reading does not trigger an alert if it lacks spatial consistency with other sensors. The confidence threshold is configurable, and the system adapts its baseline over time to account for gradual routine changes."

### Q3: Why MQTT over REST for sensor communication?

**Answer:** "MQTT is designed for IoT — it is lightweight, uses minimal bandwidth, supports publish/subscribe patterns, maintains persistent connections, and handles unreliable networks gracefully. REST requires the client to poll constantly, which drains battery on old devices. MQTT lets the device publish frames as they happen and receive commands without polling. It is the industry standard for IoT sensor communication."

### Q4: How does the system handle privacy?

**Answer:** "All processing happens locally — video frames are processed on the AI hub within your own network, not sent to external cloud services. The only external call is to Claude for narrative generation, and even that sends structured event data, not raw video. All clips are stored locally with configurable retention policies. Users can delete their data at any time. In demo mode, no external calls are made at all."

### Q5: What does the clip extraction save compared to a traditional DVR?

**Answer:** "A traditional DVR records everything 24/7 and stores terabytes of footage, most of which is empty rooms. Our Smart Clip Extraction Engine records nothing during normal activity. It only assembles a clip when an anomaly is confirmed, pulling pre-event frames from a ring buffer. The result is a focused 10-20 second clip that captures exactly the suspicious event. Storage requirements drop from terabytes to megabytes."

### Q6: How does the prediction engine work?

**Answer:** "We have a scenario library of intrusion behavioral signatures based on criminology research. Each scenario has defined phases — for example, an intrusion typically starts with casing (repeated passes along the perimeter), then entry probing (testing doors and windows), then reconnaissance, then intrusion. As live sensor events arrive, we score them against each phase signature. When early phases match with sufficient confidence, we raise a predictive alert before the final event occurs."

### Q7: How much does it cost to deploy?

**Answer:** "For a typical home: zero hardware cost since it uses existing old devices. The software is self-hosted. The only paid service is the Claude API for narrative generation, which costs approximately $3-5 per month at typical home usage levels. The MQTT broker, YOLO inference, and all other processing runs locally. In demo mode, it costs nothing at all."

### Q8: Can it scale to apartment buildings?

**Answer:** "Yes. The architecture is designed with sensor nodes publishing to an MQTT broker, which can be scaled horizontally. Each apartment would have its own baseline profile and alert configuration. The database can be migrated from SQLite to PostgreSQL for multi-tenant deployments. The prediction engine and anomaly detection run independently per tenant."

### Q9: Does it work offline?

**Answer:** "The core system — sensor streaming, YOLO detection, anomaly scoring, clip extraction — works entirely offline. The only feature that requires internet is the Claude API for generating AI narratives, and we have pre-written fallback templates for that. Push notifications via FCM require internet, but the system logs alerts locally regardless."

### Q10: What about GDPR and data residency?

**Answer:** "All data is stored locally on the AI hub. Video frames are processed and discarded — only anomaly clips are saved, and those have configurable retention policies. Users can request deletion of all their data. We do not use any third-party analytics. The only external data transmission is structured event data to the Claude API, which can be disabled entirely."

### Q11: What makes this different from existing smart home security products?

**Answer:** "Three things. First, zero hardware cost — we repurpose old devices instead of requiring proprietary cameras. Second, behavioral intelligence — we learn what is normal for each specific home instead of using generic motion detection. Third, predictive capability — we can detect the casing phase of an intrusion before it happens. No consumer product currently offers behavioral prediction."

### Q12: Can the system be fooled?

**Answer:** "Like any system, it has limitations. Someone who moves exactly like a household member in exactly the right zones at exactly the right times could theoretically avoid detection. However, the multi-sensor fusion and trajectory matching make this extremely difficult. The baseline adapts over time, and the prediction engine adds another layer by matching behavioral sequences against known intrusion patterns rather than just individual events."

---

## 16. 3-Minute Pitch Script

### [0:00 - 0:20] Hook

"What if your old phone — the one sitting in a drawer right now — could protect your home? Not with a motion sensor that screams at every shadow, but with an AI that actually understands your home's daily rhythm and knows when something does not belong."

### [0:20 - 0:50] The Problem

"Traditional security cameras have a fundamental problem: they detect motion, not meaning. They cannot tell the difference between your cat walking through the kitchen at 3 AM and a stranger doing the same thing. The result? Thousands of false alerts that homeowners learn to ignore. And when a real threat happens, you are left scrubbing through hours of footage to find 10 seconds of evidence. We built something different."

### [0:50 - 1:30] Solution Demo

"HomeGuardian AI turns old devices into intelligent sensors. This old phone is streaming to our AI hub right now. For the first two weeks, the system just watches and learns — it builds a complete behavioral fingerprint of the home. After that, watch what happens..."

[Demo: Start Scenario B — Late Night Anomaly]

"Motion at 2:43 AM in the living room. The system knows this zone has zero activity at this hour. It instantly captures a clip, writes an incident narrative — not 'Motion Detected' but a full explanation of why this is suspicious — assigns a risk score of 78, and sends everything to my phone. All in under 3 seconds."

### [1:30 - 2:10] Secret Weapon — Live Demo

"But here is our secret weapon."

[Demo: Start Scenario C or D — Casing/Intrusion Prediction]

"Most break-ins follow a pattern. The intruder cases the property first. Watch — the system just detected repeated passes along the front perimeter. It matches this against known intrusion behavioral signatures. Before anyone has even tried a door or window, the system is already warning me: 73% match to casing behavior, predicted next phase: entry probing. We catch intrusions BEFORE they start."

### [2:10 - 2:40] Scale and Use Cases

"And the best part? Zero hardware cost. Old phones, old webcams, old CCTV — any device with a camera and internet becomes a smart sensor. Scale this to apartment buildings, university campuses, small businesses. The behavioral baseline adapts to each environment. The AI gets smarter every day."

### [2:40 - 3:00] Call to Action

"We don't detect motion — we detect intent. HomeGuardian AI: the AI that knows your home better than a stranger ever could. Thank you."

---

## 17. Demo Preparation Checklist

Before presenting to judges:

- [ ] Confirm demo mode is activated (DEMO_MODE=true)
- [ ] Run the diagnostics script — all tests should pass
- [ ] Load Scenario A first to show normal baseline behavior
- [ ] Verify Scenario D (Full Intrusion Prediction) runs completely
- [ ] Test theme toggle (dark to light and back)
- [ ] Confirm the floor plan heat zones animate correctly
- [ ] Verify the AI narrative modal opens with full text
- [ ] Test the risk score gauge animation
- [ ] Confirm push notification simulation works
- [ ] Have the pitch script open on a separate device
- [ ] Close all unnecessary browser tabs and applications
- [ ] Set screen brightness to maximum
- [ ] Mute all other notifications on the demo device
- [ ] Have a backup plan: if the live demo fails, use the pre-recorded clips
