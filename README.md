# 🌾 AI Crop Insurance Agent

**Autonomous AI agent that monitors real-time weather data, detects natural disasters using machine learning, and automatically triggers insurance payouts on the Flare blockchain.**

Built at [ETH Oxford 2026](https://ethoxford.com) 🏫

---

## The Problem

Over 500 million smallholder farmers worldwide lack access to crop insurance. Traditional insurance is slow, expensive, and requires manual claims processing. When a drought or flood destroys crops, farmers wait weeks or months for payouts — if they get them at all.

## The Solution

An AI-powered insurance agent that runs 24/7:

1. **Fetches real-time weather data** from the Open-Meteo API (temperature, rainfall, humidity, wind speed + 14-day history)
2. **Detects disasters using an ML ensemble** — a rule-based detector and an Isolation Forest must BOTH agree before a disaster is declared (reduces false alarms)
3. **Automatically triggers smart contract payouts** on Flare's blockchain — no manual claims, no paperwork, no delays
4. **Live dashboard** shows current conditions, AI assessments, weather charts, and on-chain policy status

## How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  Open-Meteo  │────▶│  AI Ensemble     │────▶│  Smart Contract   │
│  Weather API │     │  (Rules + ML)    │     │  on Flare Coston2 │
└─────────────┘     └──────────────────┘     └───────────────────┘
      │                     │                         │
      │              ┌──────┴──────┐                  │
      │              │             │                  │
      │         Rule-Based    Isolation          Auto-Payout
      │         Detector      Forest             to Farmer
      │              │             │                  │
      └──────────────┴─────────────┴──────────────────┘
                            │
                    ┌───────┴───────┐
                    │   Streamlit   │
                    │   Dashboard   │
                    └───────────────┘
```

### AI Ensemble Approach

The disaster detector uses **two independent methods** that must both agree:

**Detector A — Rule-Based Thresholds:**
- Drought: < 2mm total rain over 10 days
- Flood: > 50mm current rainfall
- Frost: Temperature < 2°C
- Heat Wave: Temperature > 45°C

**Detector B — Isolation Forest (scikit-learn):**
- Trains on 14 days of historical weather data
- Features: max temp, min temp, rainfall, wind speed
- Flags statistically anomalous weather patterns
- Uses contamination parameter of 0.1

**Ensemble Logic:** Both detectors must agree → disaster declared → smart contract payout triggered. This reduces false positives significantly compared to using either method alone.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Weather Data | [Open-Meteo API](https://open-meteo.com/) (free, no API key) |
| ML Model | scikit-learn (Isolation Forest) + NumPy |
| Blockchain | Solidity ^0.8.20, Hardhat, web3.py |
| Network | Flare Testnet Coston2 (Chain ID: 114) |
| Dashboard | Streamlit + Plotly |
| Language | Python 3.10+, Solidity, TypeScript |

## Project Structure

```
crop-insurance-ai/
├── weather_fetcher.py      # Box 1: Fetches real-time weather from Open-Meteo
├── disaster_detector.py    # Box 2: ML ensemble (rules + Isolation Forest)
├── agent.py                # Box 4: Autonomous agent loop
├── dashboard.py            # Box 5: Streamlit dashboard
├── CropInsurance.json      # Contract ABI (auto-generated)
├── contracts/              # Hardhat project
│   ├── src/
│   │   └── CropInsurance.sol   # Box 3: Insurance smart contract
│   ├── scripts/
│   │   └── deploy.ts           # Deployment script
│   ├── hardhat.config.ts
│   └── .env                    # Private key (DO NOT COMMIT)
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- MetaMask browser extension
- Git

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/crop-insurance-ai.git
cd crop-insurance-ai
pip install requests scikit-learn numpy pandas web3 streamlit plotly
```

### 2. Set up Flare testnet

Add Coston2 to MetaMask:
- **RPC URL:** `https://coston2-api.flare.network/ext/C/rpc`
- **Chain ID:** `114`
- **Symbol:** `C2FLR`
- **Explorer:** `https://coston2-explorer.flare.network`

Get free test tokens at [faucet.flare.network/coston2](https://faucet.flare.network/coston2)

### 3. Deploy the smart contract

```bash
cd contracts
npm install
cp .env.example .env
# Edit .env and add your private key: PRIVATE_KEY=your_key_here
npx hardhat compile
npx hardhat run scripts/deploy.ts --network coston2
```

Copy the deployed contract address.

### 4. Configure and run the agent

Edit `agent.py` — paste your contract address and private key in the CONFIG section at the top.

```bash
cd ..
python agent.py
```

The agent will create a test policy, fund the contract, and start monitoring weather every 60 seconds.

### 5. Run the dashboard

In a new terminal:

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501`. You can:
- View real-time weather for multiple locations
- See the AI's disaster assessment (rules + ML)
- Click "Simulate Drought/Flood/Frost" buttons for demo
- View 14-day weather history charts
- Check on-chain policy status

## Smart Contract

Deployed on **Flare Testnet Coston2**.

| Function | Description |
|----------|-------------|
| `createPolicy(location)` | Farmer pays premium, gets 3x payout coverage |
| `declareDisaster(policyId, type)` | Agent-only: triggers automatic payout to farmer |
| `policyCount()` | Returns total number of policies |
| `receive()` | Accepts funding for the insurance pool |

The contract ensures each policy can only be paid out **once** — after a disaster is declared, the policy is marked as claimed and deactivated.

## Demo

1. Run `python agent.py` in one terminal — shows live weather monitoring
2. Run `streamlit run dashboard.py` in another — shows the visual dashboard
3. Click "Simulate Drought" to see the AI detect a disaster
4. Check the contract on [Coston2 Explorer](https://coston2-explorer.flare.network) to verify on-chain transactions

## Flare Building Experience

This was my first time building on Flare (and on any blockchain). The Coston2 testnet was straightforward to set up — adding the RPC endpoint to MetaMask and getting test tokens from the faucet took under 5 minutes. The flare-hardhat-starter kit made contract deployment simple.

Flare's enshrined data protocols (FTSO, FDC) are a natural fit for parametric insurance — the ability to bring verified external data (like weather) on-chain through the Flare Data Connector is exactly what this use case needs. For a production version, FDC's Web2Json attestation type would allow weather data to be cryptographically verified on-chain rather than relying on a trusted agent.

## Future Work

- **FDC Integration:** Use Flare Data Connector to bring weather data on-chain with cryptographic proofs
- **FTSO Price Feeds:** Denominate policies in USD using Flare's native price oracle
- **Multi-region:** Scale to monitor thousands of farm locations simultaneously
- **Advanced ML:** Add LSTM time-series forecasting for early warning predictions
- **FAssets:** Enable cross-chain premium payments (BTC, XRP, DOGE)

