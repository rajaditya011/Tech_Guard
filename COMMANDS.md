# HomeGuardian AI — User Command Shortcuts

**This file is for the HUMAN ONLY.** Copy-paste these commands directly into any AI chat. No additional context needed — the AI will read the project files and understand what to do.

---

## Setup and Build Commands

| Command                                           | What It Does                                                |
| ------------------------------------------------- | ----------------------------------------------------------- |
| Execute Chunk 00                                  | Creates the build manifest and diagnostics script           |
| Execute Chunk 01                                  | Sets up folder structure, installs all dependencies          |
| Execute Chunk 02                                  | Builds the FastAPI backend core (DB, auth, MQTT, WebSocket) |
| Execute Chunk 03                                  | Builds the sensor data pipeline and streaming               |
| Execute Chunk 04                                  | Builds the ML and anomaly detection engine                  |
| Execute Chunk 05                                  | Builds the intelligence response layer (clips, Claude, alerts)|
| Execute Chunk 06                                  | Builds the React frontend shell and design system           |
| Execute Chunk 07                                  | Builds the Old Device Portal                                |
| Execute Chunk 08                                  | Builds the New Device Dashboard                             |
| Execute Chunk 09                                  | Builds the secret weapon, security hardening, and deployment|
| Build everything from scratch                     | Executes all chunks in dependency order (00 through 09)     |
| Run diagnostics                                   | Runs the diagnostics script to check all systems            |

---

## Fix Commands

| Command                                                   | What It Does                                           |
| --------------------------------------------------------- | ------------------------------------------------------ |
| The backend won't start — fix it                          | Diagnoses and fixes FastAPI startup errors              |
| WebSocket not connecting — fix it                         | Fixes WebSocket connection issues                      |
| The old device portal is not streaming — fix it           | Fixes camera stream and MQTT connection issues          |
| Anomaly detection is not firing — fix it                  | Debugs the anomaly detection pipeline                  |
| MQTT messages are not being received — fix it             | Fixes MQTT broker connection and subscription issues    |
| The floor plan heat zones are not updating — fix it       | Fixes floor plan data flow and rendering               |
| Push notifications are not arriving — fix it              | Fixes FCM configuration and delivery                   |
| The risk score gauge is not animating — fix it            | Fixes the arc gauge animation component                |
| Clip extraction is not generating MP4 files — fix it      | Fixes the clip encoding and storage pipeline           |

---

## UI/UX Change Commands

| Command                                                   | What It Does                                           |
| --------------------------------------------------------- | ------------------------------------------------------ |
| Switch to light theme                                     | Activates the light theme across all components         |
| Switch to dark theme                                      | Activates the dark theme across all components          |
| Redesign the floor plan visualizer                        | Creates a new floor plan component design              |
| Make the alert cards more compact                         | Reduces alert card size and whitespace                 |
| Add a glassmorphism effect to the dashboard cards         | Applies glass effect to all dashboard surfaces          |
| Make the sidebar collapsible                              | Adds collapse/expand toggle to the sidebar             |
| Improve the mobile responsive layout                      | Optimizes layouts for mobile screens                   |
| Make the camera feed grid 2x2 instead of 3x3             | Changes the live feed grid layout                      |
| Add a loading skeleton to the dashboard                   | Adds skeleton loading states to all panels             |

---

## Feature Commands

| Command                                                           | What It Does                                    |
| ----------------------------------------------------------------- | ----------------------------------------------- |
| Add a new sensor node type: [name]                                | Extends the sensor node model with new type     |
| Add email alerts                                                  | Adds email notification channel to alert system |
| Add voice warning playback on old device                          | Implements audio playback on old device portal  |
| Add a timeline view for anomaly history                           | Creates a chronological anomaly timeline        |
| Add zone editing to the floor plan                                | Allows dragging/resizing zones on the floor plan|
| Add PDF export for incident reports                               | Generates downloadable PDF from AI narratives   |
| Add multi-language support                                        | Implements i18n for the dashboard               |
| Add a sensor node battery level indicator                         | Displays battery status for mobile sensors      |

---

## Demo Commands

| Command                                                   | What It Does                                           |
| --------------------------------------------------------- | ------------------------------------------------------ |
| Start the intrusion simulation demo                       | Runs Scenario D (Full Intrusion Prediction)            |
| Prepare for a live judge demo                             | Sets up demo mode, loads all scenarios, runs diagnostics|
| Load the casing scenario                                  | Runs Scenario C (Casing Simulation)                    |
| Run the normal routine demo                               | Runs Scenario A (Normal Morning Routine)               |
| Run the late night anomaly demo                           | Runs Scenario B (Late Night Anomaly)                   |
| Show me the AI reasoning timeline                         | Displays the prediction engine reasoning replay         |
| Reset demo to clean state                                 | Clears all demo data and returns to initial state       |

---

## Deployment Commands

| Command                                                   | What It Does                                           |
| --------------------------------------------------------- | ------------------------------------------------------ |
| Deploy to Cloud Run                                       | Builds and deploys all services to Google Cloud Run     |
| Build Docker images                                       | Builds all Docker images for production                |
| Start local development environment                       | Starts all services locally with docker-compose        |
| Start only the backend                                    | Runs FastAPI dev server only                           |
| Start only the frontend                                   | Runs Vite dev server only                              |
| Start the MQTT broker                                     | Starts Eclipse Mosquitto locally                       |

---

## Emergency Commands

| Command                                                           | What It Does                                    |
| ----------------------------------------------------------------- | ----------------------------------------------- |
| Everything is broken — start fresh                                | Resets the project and rebuilds from Chunk 00   |
| I have 30 minutes before demo — make it work                     | Focuses on demo-critical features only          |
| I have 10 minutes before demo — make it work                     | Starts demo mode with synthetic data only       |
| The demo crashed mid-presentation — recover NOW                  | Restarts services and resumes demo scenario     |

---

## Meta Commands

| Command                                                   | What It Does                                           |
| --------------------------------------------------------- | ------------------------------------------------------ |
| What is the current build status?                         | Reports which chunks are complete/incomplete           |
| What features are working?                                | Lists all functional features                          |
| Explain the anomaly detection pipeline                    | Provides a technical walkthrough of F02-F04            |
| Explain the prediction engine                             | Provides a technical walkthrough of F11                |
| Show me the architecture diagram                          | Displays the system architecture                       |
| What API keys do I need?                                  | Lists required API keys and how to get them            |
| Run a security audit                                      | Reviews the project against SECURITY_CHECKLIST.md      |

---

## Usage Tips

1. **Copy the exact command text** from the "Command" column and paste it into any AI chat (Claude, Gemini, GPT, etc.).
2. **Make sure your project files are accessible** to the AI — either via file upload, workspace, or repository link.
3. **The AI will read README.md and CHANGELOG.md first** to understand the project state before executing your command.
4. **Replace bracketed text** like `[name]` with your actual value before pasting.
5. **For emergency commands**, the AI will prioritize the most critical path to a working demo.
6. **Commands can be combined**: "Execute Chunk 02 and then Execute Chunk 03" works fine.
7. **If the AI asks for clarification**, provide it — these commands are starting points, not rigid scripts.
