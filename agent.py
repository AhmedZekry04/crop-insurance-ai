import time
import json
from web3 import Web3
from weather_fetcher import get_weather
from disaster_detector import DisasterDetector

# ===== CONFIG — FILL THESE IN =====
CONTRACT_ADDRESS = "0x6A0088D3885b0Ea10a0bCF9bb9938140DfeD1Dad"
PRIVATE_KEY = "9cdaa582ad83686217ef92553164f819c3305c739a7decb53e4631665c02c6a5"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"

# Locations to monitor
MONITORED = [
    {"lat": -1.286, "lon": 36.817, "name": "Nairobi", "policy_id": 0},
]

# ===== SETUP =====
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Agent wallet: {account.address}")
print(f"Connected to Flare: {w3.is_connected()}")

# Load contract ABI
with open("CropInsurance.json") as f:
    artifact = json.load(f)
    abi = artifact["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
detector = DisasterDetector()

def check_location(loc):
    print(f"\nChecking {loc['name']}...")

    # Box 1: Get weather
    weather = get_weather(loc["lat"], loc["lon"])
    current = weather["current"]
    daily = weather["daily"]
    print(f"  Temp: {current['temperature_2m']}C | Rain: {current['rain']}mm")

    # Train if needed
    if not detector.is_trained:
        detector.train(daily)

    # Box 2: Detect
    result = detector.detect(current, daily)
    print(f"  Rule: {result['rule_detector']['result']} | ML: {result['ml_detector']['result']}")

    if result["disaster"]:
        print(f"  DISASTER: {result['type']}")
        trigger_payout(loc["policy_id"], result["type"])
    else:
        print(f"  All normal")

    return result

def trigger_payout(policy_id, disaster_type):
    try:
        tx = contract.functions.declareDisaster(
            policy_id, disaster_type
        ).build_transaction({
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
        })
        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"  Payout TX: {tx_hash.hex()}")
    except Exception as e:
        print(f"  Payout failed: {e}")

def create_test_policy():
    """Create a test policy so we have something to trigger"""
    print("Creating test policy for Nairobi...")
    tx = contract.functions.createPolicy("Nairobi, Kenya").build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "value": w3.to_wei(1, "ether"),
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"  Policy created! TX: {tx_hash.hex()}")

    # Fund the contract so it can pay out
    print("Funding contract with 5 C2FLR...")
    fund_tx = {
        "from": account.address,
        "to": CONTRACT_ADDRESS,
        "value": w3.to_wei(5, "ether"),
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 21000,
        "gasPrice": w3.eth.gas_price,
        "chainId": 114
    }
    signed = w3.eth.account.sign_transaction(fund_tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"  Funded! TX: {tx_hash.hex()}")

if __name__ == "__main__":
    # First run: create a test policy
    policy_count = contract.functions.policyCount().call()
    if policy_count == 0:
        create_test_policy()

    print("\nAgent running — checking every 60 seconds (Ctrl+C to stop)")
    while True:
        for loc in MONITORED:
            check_location(loc)
        print("\nSleeping 60s...")
        time.sleep(60)