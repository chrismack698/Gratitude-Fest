# Gratitude Fest — Technical Architecture

> End-to-end data flow across two Snowflake accounts — from donor eligibility through real-time thanking to Salesforce Activity records.

| | |
|---|---|
| **Accounts** | Data Warehouse ← internal data share → App Account |
| **Queue refresh** | Daily at 5:00 AM CST |
| **Interface** | Streamlit in Snowflake (AD-restricted) |

---

## System Diagram

```mermaid
flowchart TD
    classDef dw     fill:#1e3a5f,stroke:#3B82F6,color:#93c5fd
    classDef app    fill:#5a1e1e,stroke:#EF4444,color:#fca5a5
    classDef proc   fill:#1a3d28,stroke:#22C55E,color:#86efac
    classDef task   fill:#3a1a5f,stroke:#A855F7,color:#d8b4fe
    classDef share  fill:#3d2e0e,stroke:#F59E0B,color:#fcd34d
    classDef email  fill:#0a2d36,stroke:#06B6D4,color:#67e8f9
    classDef sf     fill:#3d2010,stroke:#F97316,color:#fdba74
    classDef table  fill:#1e2334,stroke:#374151,color:#9ca3af

    subgraph DW ["❄  DATA WAREHOUSE ACCOUNT"]
        direction TB
        P1["🔄 UPDATE_FEST_QUEUE() Stored Procedure Runs @ 5AM CST"]:::dw
        DWT["📋 FEST_QUEUE Table · Data Warehouse"]:::table
        P1 -->|"writes eligible donors"| DWT
    end

    DS1{{"⇄ Internal Data Share"}}:::share

    subgraph APP ["❄  APP ACCOUNT"]
        direction TB
        T1["⏰ insert_fest_queue_task Scheduled Task — runs each morning"]:::task
        APT["📋 FEST_QUEUE Table · App Account"]:::table
        T1 -->|"INSERT_FEST_QUEUE_PROC de-duped insert"| APT

        STR["🖥 Streamlit App AD group access only"]:::app
        APT -->|"donors available"| STR

        STR --> C1["📞 Claim Next Donor Assigns donor to user Writes claim to audit log"]:::proc
        STR --> C2["✅ Mark Thanked Marks donor · saves notes Writes history to audit log"]:::proc
        STR --> C3["💬 App Feedback Captures user feedback"]:::proc

        AL["📜 AUDIT_LOG Table · App Account"]:::table
        C1 -->|"writes claim"| AL
        C2 -->|"writes history"| AL

        FB["📋 APP_FEEDBACK Table · App Account"]:::table
        C3 -->|"writes feedback"| FB

        EM["📧 Email Notifications"]:::email
        C2 -->|"donor notes"| EM
        C3 -->|"feedback copy"| EM

        T2["⏰ CALL_UPDATE_GRATITUDE_FEST_RESULTS Scheduled Task — runs throughout day"]:::task
        APT -->|"thanked donors"| T2
        T2 -->|"UPDATE_GRATITUDE_FEST_RESULTS()"| RES

        RES["📋 GRATITUDE_FEST_RESULTS Table · App Account"]:::table
    end

    DS2{{"⇄ Internal Data Share Results + Feedback → DW"}}:::share

    subgraph REPORT ["  RESULTS & REPORTING · DATA WAREHOUSE"]
        direction LR
        DWR["📊 GRATITUDE_FEST_RESULTS Data Warehouse"]:::table
        DWF["📋 APP_FEEDBACK Data Warehouse"]:::table
        RPT["📈 Campaign Reporting Dashboards & Analytics"]:::dw
        EP["📧 Email Procedure Notes & feedback distribution"]:::email
        DWR --> RPT
        DWF --> EP
    end

    SF["☁ Salesforce CRM Activity Records via REST API ⚠ Planned — next milestone"]:::sf

    DWT -->|"data share"| DS1
    DS1 -->|"ingested by task"| T1
    RES --> DS2
    FB  --> DS2
    DS2 --> DWR
    DS2 --> DWF
    RPT -->|"SF stored procedure (future)"| SF
```

---

## Flow Walkthrough

### Step 01 — Donor Queue Generation
Each active campaign day at 5:00 AM CST, `UPDATE_FEST_QUEUE()` evaluates donor eligibility and writes qualified records to `FEST_QUEUE` in the Data Warehouse.

**Objects:** `UPDATE_FEST_QUEUE()` · `FEST_QUEUE` (Data Warehouse)

---

### Step 02 — Internal Data Share
The Data Warehouse queue table is shared to the App Account via Snowflake's internal data sharing. `insert_fest_queue_task` runs each morning, calling `INSERT_FEST_QUEUE_PROC` to ingest new records with de-duplication.

**Objects:** `insert_fest_queue_task` · `INSERT_FEST_QUEUE_PROC` · Internal Data Share

---

### Step 03 — Streamlit App Interface
Users access the Streamlit app in the App Account. Access is restricted to an Active Directory group. Three stored procedures power all user actions.

**Objects:** Streamlit in Snowflake · Active Directory group

---

### Step 04 — Three Core Procedures
- **Claim Next Donor** — assigns a donor to the requesting user and logs the claim.
- **Mark Thanked** — marks the donor, saves notes, writes audit history, and sends notes by email.
- **App Feedback** — captures in-app feedback and sends a copy by email.

**Objects:** `CLAIM_NEXT()` · `MARK_THANKED()` · `SUBMIT_FEEDBACK()` · `AUDIT_LOG` · `APP_FEEDBACK`

---

### Step 05 — Results Processing
`CALL_UPDATE_GRATITUDE_FEST_RESULTS` runs throughout the day, moving thanked donors into `GRATITUDE_FEST_RESULTS`. When no active campaign dates remain, all remaining queue records are finalized into the results table.

**Objects:** `CALL_UPDATE_GRATITUDE_FEST_RESULTS` task · `UPDATE_GRATITUDE_FEST_RESULTS()` · `GRATITUDE_FEST_RESULTS`

---

### Step 06 — Results → Data Warehouse
`GRATITUDE_FEST_RESULTS` and `APP_FEEDBACK` are shared back to the Data Warehouse account via a second internal data share. Reporting dashboards and the email distribution procedure are built on these tables.

**Objects:** Internal Data Share · `GRATITUDE_FEST_RESULTS` (DW) · `APP_FEEDBACK` (DW)

---

### Step 07 — Salesforce Integration *(Planned)*
A future stored procedure will read from `GRATITUDE_FEST_RESULTS` and call the Salesforce REST API to write an Activity record for every account that was thanked — closing the loop in CRM.

**Objects:** SF Activity Procedure *(not yet built)* · Salesforce REST API

---

## Stored Procedure Reference

| Procedure | Trigger | Actions | Outputs |
|---|---|---|---|
| `Claim Next Donor` | User clicks "Claim Next Donor" in Streamlit | Selects next available donor from `FEST_QUEUE` and assigns to the requesting user | Claim written to `AUDIT_LOG` |
| `Mark Thanked` | User marks a donor as thanked | Marks donor in queue (preventing reassignment), saves notes, writes full activity history to audit log, sends notes via email | `FEST_QUEUE` updated · `AUDIT_LOG` entry · Email notification |
| `App Feedback` | User submits in-app feedback form | Writes feedback record to `APP_FEEDBACK` table, triggers email notification with feedback content | `APP_FEEDBACK` record · Email notification |
| `INSERT_FEST_QUEUE_PROC` | Called by `insert_fest_queue_task` each morning | Reads from DW data share, inserts any donors not already present in App Account `FEST_QUEUE` | `FEST_QUEUE` (App Account) populated |
| `UPDATE_GRATITUDE_FEST_RESULTS` | Called by `CALL_UPDATE` task throughout the day | Moves thanked donors to results table during campaign; finalizes all records when no active dates remain | `GRATITUDE_FEST_RESULTS` populated |
| `SF Activity Procedure` *(Planned)* | Post-campaign trigger (TBD) | Reads `GRATITUDE_FEST_RESULTS`, calls Salesforce REST API to create an Activity record per thanked account | Salesforce Activity records |

---

*Salesforce integration — next milestone*
