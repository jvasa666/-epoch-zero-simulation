# streamlit_app.py
import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import json

# Import the refactored simulation core
from mothe_simulation_core import (
    run_simulation_step,
    GRID_NODES,
    SIM_INTERVAL_SECONDS,
    BCP_GENERATION_RATE_PER_MWH_GRID_FLOW,
    OIL_GENERATION_RATE_PER_BARREL_FOR_BCP,
    BCP_RECIPIENT_ADDRESS
)

st.set_page_config(layout="wide", page_title="Epoch Zero Mainnet Simulation")

# --- Streamlit UI Setup ---
st.title("🔥 Epoch Zero Mainnet Simulation 🔥")
st.subheader("Live Operational Dashboard")

st.markdown(
    """
    Welcome, Commander. This dashboard provides a live, real-time view of the Epoch Zero Simulation.
    Monitor energy flows, resource discovery, security alerts, and system activities
    as our new world comes to life.
    """
)

# Initialize session state for the simulation
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'sim_results' not in st.session_state:
    st.session_state.sim_results = {
        "energy": {"total_mwh": 0.0},
        "gold": 0.0,
        "oil": 0.0,
        "nuclear_signatures": 0,
        "anomalies": [],
        "supply_chain": [],
        "orbital": [],
        "ids": [],
        "bcp_transactions": [], # For simulated BCP logs
        "logs": [], # For live operational logs
        "current_sim_time": datetime.utcnow().isoformat(), # Track simulation time
        "sim_step_count": 0,
        "solar_nodes": None, # Will store instances of SolarNodeController
        "distribution_nodes": None, # Will store instances of UniversalDistributionNode
        "asp": None, # Will store instance of AISovereigntyProtocol
    }

# Ensure persistent objects are initialized only once
if st.session_state.sim_results['solar_nodes'] is None:
    from mothe_simulation_core import SolarNodeController, UniversalDistributionNode, AISovereigntyProtocol
    st.session_state.sim_results['solar_nodes'] = [SolarNodeController(region) for region in GRID_NODES]
    st.session_state.sim_results['distribution_nodes'] = [UniversalDistributionNode(name) for name in GRID_NODES]
    st.session_state.sim_results['asp'] = AISovereigntyProtocol()


# Controls for the simulation
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("Start Simulation", disabled=st.session_state.simulation_running):
        st.session_state.simulation_running = True
        st.session_state.sim_results['current_sim_time'] = datetime.utcnow().isoformat()
        st.info("Simulation started...")
        st.rerun() # Rerun to update button state
with col2:
    if st.button("Stop Simulation", disabled=not st.session_state.simulation_running):
        st.session_state.simulation_running = False
        st.warning("Simulation stopped.")
        st.rerun() # Rerun to update button state

# Create placeholders for live updates
kpis_placeholder = st.empty()
charts_placeholder = st.empty()
log_placeholder = st.empty()
detailed_output_placeholder = st.empty()


# --- Simulation Loop ---
if st.session_state.simulation_running:
    # Use a loop with time.sleep for continuous updates
    # The 'with st.empty():' pattern ensures elements update in place
    # A single placeholder can be used for the entire dashboard layout to enforce updates
    
    with st.container(): # Use a container to group all dynamic elements
        while st.session_state.simulation_running:
            # Advance simulation time
            sim_time_obj = datetime.fromisoformat(st.session_state.sim_results['current_sim_time'])
            sim_time_obj += timedelta(seconds=SIM_INTERVAL_SECONDS)
            st.session_state.sim_results['current_sim_time'] = sim_time_obj.isoformat()
            st.session_state.sim_results['sim_step_count'] += 1

            # Run one simulation step
            st.session_state.sim_results = run_simulation_step(
                st.session_state.sim_results,
                sim_time_obj,
                SIM_INTERVAL_SECONDS
            )

            # --- Update KPIs ---
            with kpis_placeholder.container():
                st.markdown("### Key Operational Metrics")
                kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
                with kpi_col1:
                    st.metric(label="Total Energy Generated (MWh)", value=f"{st.session_state.sim_results['energy']['total_mwh']:.2f}")
                with kpi_col2:
                    st.metric(label="Total Gold Discovered", value=f"{st.session_state.sim_results['gold']:.4f}")
                with kpi_col3:
                    st.metric(label="Total Oil Discovered (Barrels)", value=f"{st.session_state.sim_results['oil']:.4f}")
                with kpi_col4:
                    st.metric(label="Nuclear Signatures", value=st.session_state.sim_results['nuclear_signatures'])

                st.markdown(f"**Simulated Time:** {sim_time_obj.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                st.markdown(f"**Simulation Step:** {st.session_state.sim_results['sim_step_count']}")


            # --- Update Charts (Example: Energy Distribution) ---
            with charts_placeholder.container():
                st.markdown("### Energy Distribution Across Regions")
                # Prepare data for energy distribution chart
                energy_data = []
                for node in st.session_state.sim_results['distribution_nodes']:
                    energy_data.append({"Region": node.region_name, "Energy Balance (MWh)": node.energy_balance})
                df_energy = pd.DataFrame(energy_data)
                st.bar_chart(df_energy.set_index("Region"))

                # Example: Historical MWh generated (simple list)
                # For a true time series, you'd store MWh per step in a list.
                # For now, let's just show total accumulating MWh
                st.line_chart(pd.DataFrame({'Total MWh': [st.session_state.sim_results['energy']['total_mwh']]}), use_container_width=True)

            # --- Live Operational Log ---
            with log_placeholder.container():
                st.markdown("### Live Operational Log")
                # Display the last few log entries
                for log_entry in reversed(st.session_state.sim_results['logs']): # Show most recent first
                    st.text(log_entry)
                
                # To make the log update smoothly without flickering, we might need a fixed height text area
                # st.text_area("Operational Log", value="\n".join(st.session_state.sim_results['logs']), height=300)


            # --- Detailed Status ---
            with detailed_output_placeholder.container():
                st.markdown("### Detailed System Status")
                st.json(st.session_state.sim_results) # Display raw results for debugging/detail

            # Introduce a small delay to control update speed and reduce CPU usage
            time.sleep(0.5) # Update every 0.5 seconds for a smooth display

            # Re-run the script to update the UI
            st.rerun()

else:
    # Display current state when simulation is stopped
    st.info("Simulation is currently stopped. Press 'Start Simulation' to begin.")
    
    st.markdown("### Current Simulation State (Stopped)")
    if st.session_state.sim_results:
        st.metric(label="Total Energy Generated (MWh)", value=f"{st.session_state.sim_results['energy']['total_mwh']:.2f}")
        st.metric(label="Total Gold Discovered", value=f"{st.session_state.sim_results['gold']:.4f}")
        st.metric(label="Total Oil Discovered (Barrels)", value=f"{st.session_state.sim_results['oil']:.4f}")
        st.metric(label="Nuclear Signatures", value=st.session_state.sim_results['nuclear_signatures'])
        st.markdown(f"**Last Simulated Time:** {datetime.fromisoformat(st.session_state.sim_results['current_sim_time']).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        st.markdown(f"**Last Simulation Step:** {st.session_state.sim_results['sim_step_count']}")

        st.markdown("---")
        st.markdown("### Full Simulation Results (JSON Preview)")
        st.json(st.session_state.sim_results)

# Final BCP calculation and "simulated" distribution log if a full cycle were completed
# This part would typically be triggered after a specific duration (e.g., DAYS_TO_SIMULATE_FOR_RESOURCE_FLOW)
# For this live dashboard, we'll just show the calculation based on current totals.
total_mwh_for_bcp = st.session_state.sim_results['energy']['total_mwh']
total_oil_for_bcp = st.session_state.sim_results['oil']
bcp_total_calculated = (total_mwh_for_bcp * BCP_GENERATION_RATE_PER_MWH_GRID_FLOW) + \
                     (total_oil_for_bcp * OIL_GENERATION_RATE_PER_BARREL_FOR_BCP)
btc_send_calculated = bcp_total_calculated / 30000 # BTC price assumed 30k USD

st.markdown("---")
st.markdown("### Bitcoin-Correlated Asset (BCP) Projection")
st.info(f"Projected BCP generation: **{bcp_total_calculated:.6f} BCP** (approx. **{btc_send_calculated:.8f} BTC** equivalent)")
st.caption(f"Recipient: `{BCP_RECIPIENT_ADDRESS}` (This is a simulated calculation for display)")