# mothe_simulation_core.py
# Refactored for web dashboard integration

import random
import logging
import json
import subprocess
import time
from datetime import datetime, timedelta

# --- Configuration (can be modified externally or through UI) ---
# IMPORTANT: For live web deployment, actual bitcoin-cli calls will be disabled or simulated.
# Do NOT enable actual bitcoin-cli calls on a publicly accessible web server without
# extreme security measures and a clear understanding of the risks.

# Setup logging (will be overridden by Streamlit's logging for dashboard)
# Keeping this for local script testing if needed
logging.basicConfig(
    # filename="D:\\mothe_simulation_mainnet.log", # Commented out for web
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)

# Constants and config
# CURRENT_UTC_TIME will be dynamic in the web app
DAYS_TO_SIMULATE_FOR_RESOURCE_FLOW = 1 # This will define the "full cycle" for BCP/exports

SIM_INTERVAL_SECONDS = 1 # 1-second intervals (Instant Mode for simulation steps)

BCP_GENERATION_RATE_PER_MWH_GRID_FLOW = 0.05
OIL_GENERATION_RATE_PER_BARREL_FOR_BCP = 0.01

BCP_RECIPIENT_ADDRESS = "bcrt1qtc0jfat4wdu5wsa5xump6n4gqsn9kh32kgf9ee"

# BITCOIN_CLI_PATH = r'"C:\Program Files\Bitcoin\daemon\bitcoin-cli.exe"' # Commented for web

GRID_NODES = ["RegionAlpha", "RegionBeta", "RegionGamma"]

# --- Simulation Classes (Unchanged, as they represent core logic) ---

class SolarNodeController:
    def __init__(self, node_name):
        self.node_name = node_name
        self.irradiance = 0.0  # W/m2 simulated
        self.temperature = 25.0  # Celsius simulated
        self.panel_health = 100.0  # Percent
        self.output_power_mwh = 0.0

    def read_sensors(self):
        self.irradiance = random.uniform(800, 1200)
        self.temperature = random.uniform(15, 45)
        self.panel_health = max(80, self.panel_health - random.uniform(0, 0.01))

    def calibrate_output(self):
        base_power = (self.irradiance / 1000) * 0.3
        health_factor = self.panel_health / 100
        temp_factor = max(0.75, 1 - (self.temperature - 25) * 0.01)
        self.output_power_mwh = base_power * health_factor * temp_factor * (SIM_INTERVAL_SECONDS / 3600)
        # logging.info(f"[SOLAR] {self.node_name} output {self.output_power_mwh:.6f} MWh (irradiance {self.irradiance:.1f} W/m2, temp {self.temperature:.1f}C, health {self.panel_health:.2f}%)")
        return self.output_power_mwh

    def generate_energy(self):
        self.read_sensors()
        return self.calibrate_output()


class UniversalDistributionNode:
    def __init__(self, region_name):
        self.region_name = region_name
        self.energy_balance = 0.0

    def balance_and_distribute(self, amount):
        self.energy_balance += amount / len(GRID_NODES)
        # logging.info(f"[DISTRIBUTION] {self.region_name} distributing {self.energy_balance:.6f} MWh")
        # self.energy_balance = 0.0 # Don't zero out immediately, allow accumulation for display


class AISovereigntyProtocol:
    def __init__(self):
        # logging.info("[ASP] AI Sovereignty Protocol Initialized")
        pass

    def monitor_grid_integrity(self, threat_level):
        if threat_level > 8500:
            # logging.warning("[ASP ALERT] Threat Detected and Quarantined")
            return True
        return False


def ai_boring_search_for_gold(minutes):
    found = round(random.uniform(0, 0.002) * minutes, 6)
    # logging.info(f"[GOLD SEARCH] Found {found} units of gold")
    return found


def ai_boring_search_for_oil(minutes):
    found = round(random.uniform(0, 0.003) * minutes, 6)
    # logging.info(f"[OIL SEARCH] Found {found} barrels of oil")
    return found


def quiet_nuclear_protocol_scan(minutes):
    count = random.choice([0, 1])
    # logging.info(f"[NUCLEAR SCAN] Nuclear signatures detected: {count}")
    return count


def simulate_supply_chain(region):
    water_units = random.randint(10000, 20000)
    meds = random.choice(["antivirals", "antibiotics", "vaccines"])
    log = f"[SUPPLY_CHAIN] Delivered {water_units}L water + {meds} to {region}"
    return log


def simulate_orbital_scan(region):
    findings = random.choice([
        "Gold Vein Located",
        "Tectonic Stress Point Detected",
        "Uranium Trace Signature",
        "No Anomaly"
    ])
    log = f"[ORBITAL SCAN] Satellite scan of {region}: {findings}"
    return log


def register_sovereign_id(region):
    seed_id = f"SEED_{random.randint(1000, 9999)}_{region[:2].upper()}"
    rep_score = round(random.uniform(0.5, 1.0), 2)
    log = f"[SOVEREIGN ID] {seed_id} active in {region} (rep: {rep_score})"
    return log


# --- Wallet & BCP Functions (Simulated for Web) ---

def create_or_load_wallet_sim():
    # logging.info("[WALLET] Creating or loading wallet (simulated)")
    pass

def fund_wallet_if_needed_sim():
    # logging.info("[WALLET] Funding wallet if needed (simulated)")
    pass

def warm_up_wallet_with_blocks_sim():
    # logging.info("[WALLET] Warming up wallet by mining blocks (simulated)")
    pass

def distribute_bcp_for_resource_flow_sim(btc_amount, recipient, total_mwh, oil_amount):
    """
    Simulated BCP distribution for web dashboard.
    Does NOT call bitcoin-cli.
    """
    log = f"[DISTRIBUTE - SIMULATED] Would send {btc_amount:.8f} BTC to {recipient} (based on {total_mwh:.2f} MWh, {oil_amount:.2f} barrels oil)"
    # logging.info(log)
    return log


def export_results_sim(simulation_results_data):
    """
    Simulated export for web dashboard.
    Does NOT write to local files directly on the server for continuous updates.
    The web app will handle display.
    """
    # logging.info("[EXPORT] Simulation results prepared for display.")
    return json.dumps(simulation_results_data, indent=2)


# --- Core Simulation Step Function ---

def run_simulation_step(current_results, current_time, sim_interval_seconds):
    """
    Runs one step of the Epoch Zero simulation.
    Updates and returns the simulation results.
    """
    # Initialize objects if not already present in current_results (first run)
    if 'solar_nodes' not in current_results:
        current_results['solar_nodes'] = [SolarNodeController(region) for region in GRID_NODES]
    if 'distribution_nodes' not in current_results:
        current_results['distribution_nodes'] = [UniversalDistributionNode(name) for name in GRID_NODES]
    if 'asp' not in current_results:
        current_results['asp'] = AISovereigntyProtocol()

    solar_nodes = current_results['solar_nodes']
    distribution_nodes = current_results['distribution_nodes']
    asp = current_results['asp']

    # Initialize core metrics if not present
    if 'energy' not in current_results:
        current_results['energy'] = {'total_mwh': 0.0}
    if 'gold' not in current_results:
        current_results['gold'] = 0.0
    if 'oil' not in current_results:
        current_results['oil'] = 0.0
    if 'nuclear_signatures' not in current_results:
        current_results['nuclear_signatures'] = 0
    if 'anomalies' not in current_results:
        current_results['anomalies'] = []
    if 'supply_chain' not in current_results:
        current_results['supply_chain'] = []
    if 'orbital' not in current_results:
        current_results['orbital'] = []
    if 'ids' not in current_results:
        current_results['ids'] = []
    if 'bcp_transactions' not in current_results:
        current_results['bcp_transactions'] = []
    if 'logs' not in current_results:
        current_results['logs'] = [] # New: collect real-time logs for display

    # Generate energy from all solar nodes and sum
    generated_mwh_this_interval = sum([node.generate_energy() for node in solar_nodes])
    current_results['energy']['total_mwh'] += generated_mwh_this_interval
    current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] [ENERGY] Generated {generated_mwh_this_interval:.6f} MWh.")


    # Distribute energy
    for node in distribution_nodes:
        node.balance_and_distribute(generated_mwh_this_interval)
        # Note: self.energy_balance is *accumulating* in the node object for display clarity
        current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] [DISTRIBUTION] {node.region_name} current balance {node.energy_balance:.6f} MWh.")


    # Regional operations
    for region in GRID_NODES:
        # Simulate Supply Chain
        sc_log = simulate_supply_chain(region)
        current_results['supply_chain'].append(f"[{current_time.strftime('%H:%M:%S')}] {sc_log}")
        current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] {sc_log}")

        # Simulate Orbital Scan
        orb_log = simulate_orbital_scan(region)
        current_results['orbital'].append(f"[{current_time.strftime('%H:%M:%S')}] {orb_log}")
        current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] {orb_log}")

        # Register Sovereign ID
        id_log = register_sovereign_id(region)
        current_results['ids'].append(f"[{current_time.strftime('%H:%M:%S')}] {id_log}")
        current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] {id_log}")

    # ASP monitoring
    if asp.monitor_grid_integrity(random.uniform(1000, 9000)):
        anomaly_msg = f"[{current_time.strftime('%H:%M:%S')}] [ASP ALERT] Threat Quarantined"
        current_results['anomalies'].append(anomaly_msg)
        current_results['logs'].append(anomaly_msg)

    # Resource searches
    gold_found = ai_boring_search_for_gold(sim_interval_seconds / 60)
    oil_found = ai_boring_search_for_oil(sim_interval_seconds / 60)
    nuc_found = quiet_nuclear_protocol_scan(sim_interval_seconds / 60)

    current_results['gold'] += gold_found
    current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] [GOLD SEARCH] Found {gold_found:.6f} units of gold. Total: {current_results['gold']:.6f}")

    current_results['oil'] += oil_found
    current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] [OIL SEARCH] Found {oil_found:.6f} barrels of oil. Total: {current_results['oil']:.6f}")

    current_results['nuclear_signatures'] += nuc_found
    current_results['logs'].append(f"[{current_time.strftime('%H:%M:%S')}] [NUCLEAR SCAN] Detected {nuc_found} nuclear signatures. Total: {current_results['nuclear_signatures']}")


    # Keep logs manageable - only last 50 entries
    current_results['logs'] = current_results['logs'][-50:]

    return current_results

# NOTE: The main execution block (`if __name__ == "__main__":`) is removed
# from this core script, as it will be orchestrated by the Streamlit app.