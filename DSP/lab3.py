import streamlit as st
import networkx as nx
import random
import pandas as pd
from dataclasses import dataclass, field
from collections import Counter

# --- Model Configuration ---

# Define states for clarity
S, I, P, Q = "Susceptible", "Infected", "Patched", "Quarantined"

@dataclass
class Simulation:
    """A dataclass to hold the state of our advanced attribute-based simulation."""
    G: nx.Graph
    node_attrs: dict = field(default_factory=dict)
    time_step: int = 0
    history: list = field(default_factory=list)
    event_log: list = field(default_factory=list)
    transmissions: list = field(default_factory=list)

    def reset(self, inf_count, seed, vuln_range, cpu_speed_range, patch_delay_base, quarantine_delay_base, transmission_delay_range):
        """Initializes or resets the simulation with detailed node and edge attributes."""
        random.seed(seed)
        self.node_attrs = {}
        
        for node in self.G.nodes():
            cpu_speed = random.uniform(cpu_speed_range[0], cpu_speed_range[1])
            patch_time = int(patch_delay_base / cpu_speed)
            
            self.node_attrs[node] = {
                "state": S, "vulnerability": random.uniform(vuln_range[0], vuln_range[1]),
                "cpu_speed": cpu_speed, "patch_timer": patch_time,
                "base_patch_time": patch_time, "quarantine_timer": float('inf')
            }
            
        for edge in self.G.edges():
            self.G.edges[edge]['delay'] = random.randint(transmission_delay_range[0], transmission_delay_range[1])

        nodes_to_infect = random.sample(list(self.G.nodes()), min(inf_count, self.G.number_of_nodes()))
        for node in nodes_to_infect:
            self.node_attrs[node]["state"] = I
            self.node_attrs[node]["quarantine_timer"] = quarantine_delay_base

        self.time_step = 0
        self.history = [self.snapshot()]
        self.event_log = ["Simulation started with advanced attribute-based model."]
        self.transmissions = []

    def snapshot(self):
        """Returns a dictionary summarizing the current state of the simulation."""
        counts = Counter(attrs["state"] for attrs in self.node_attrs.values())
        return {"t": self.time_step, S: counts[S], I: counts[I], P: counts[P], Q: counts[Q]}

# --- Simulation Logic ---

def step(sim: Simulation, malware_strength: float, malware_stealth: float, quarantine_delay_base: int) -> Simulation:
    """Advances the simulation by one time step based on advanced attributes."""
    sim.time_step += 1
    newly_infected, remaining_transmissions = [], []
    
    for trans in sim.transmissions:
        if sim.time_step >= trans['arrival_time']:
            target_node = trans['target']
            target_attrs = sim.node_attrs[target_node]
            if target_attrs["state"] == S and malware_strength > target_attrs["vulnerability"]:
                newly_infected.append(target_node)
                sim.event_log.append(f"Time {sim.time_step}: ✅ Infection successful at Node {target_node} from Node {trans['source']}.")
            elif target_attrs["state"] == S:
                sim.event_log.append(f"Time {sim.time_step}: 🛡️ Infection failed at Node {target_node}. Defenses held.")
        else:
            remaining_transmissions.append(trans)
    sim.transmissions = remaining_transmissions

    for node in set(newly_infected):
        sim.node_attrs[node]["state"] = I
        sim.node_attrs[node]["quarantine_timer"] = int(quarantine_delay_base * (1 + malware_stealth))
    
    for node, attrs in sim.node_attrs.items():
        if node in newly_infected: continue
        if attrs["state"] == I:
            for neighbor in sim.G.neighbors(node):
                if sim.node_attrs[neighbor]["state"] == S and not any(t['target'] == neighbor for t in sim.transmissions):
                    delay = sim.G.edges[(node, neighbor)]['delay']
                    arrival = sim.time_step + delay
                    sim.transmissions.append({"source": node, "target": neighbor, "arrival_time": arrival})
                    sim.event_log.append(f"Time {sim.time_step}: 📡 Malware transmission started from Node {node} to Node {neighbor}. ETA: {arrival}.")
            attrs["quarantine_timer"] -= 1
            if attrs["quarantine_timer"] <= 0:
                attrs["state"] = Q
                sim.event_log.append(f"Time {sim.time_step}:  quarantined Node {node}.")
        elif attrs["state"] == S:
            attrs["patch_timer"] -= 1
            if attrs["patch_timer"] <= 0:
                attrs["state"] = P
                sim.event_log.append(f"Time {sim.time_step}: patched Node {node}.")
    sim.history.append(sim.snapshot())
    return sim

# --- NEW: File Analysis and Infection Logic ---

def analyze_file_to_get_attributes(uploaded_file):
    """Simulates analyzing a file to derive malware attributes from its properties."""
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    file_type = uploaded_file.type.split('/')[-1] if uploaded_file.type else 'unknown'

    # Determine Malware Strength from file size (0-10MB -> 0.1-1.0)
    strength = min(1.0, 0.1 + (file_size_mb / 10.0) * 0.9)

    # Determine Malware Stealth from file type
    stealth_map = {'zip': 0.7, 'pdf': 0.6, 'plain': 0.2, 'jpeg': 0.4, 'png': 0.4, 'x-msdownload': 0.9, 'octet-stream': 0.8}
    stealth = stealth_map.get(file_type, 0.5)

    return {
        "strength": round(strength, 2), "stealth": round(stealth, 2),
        "file_size_mb": round(file_size_mb, 2), "file_type": file_type
    }

def simulate_file_drop(sim: Simulation, quarantine_delay_base: int, malware_stealth: float) -> Simulation:
    """Simulates a malicious file drop on a random susceptible node."""
    susceptible_nodes = [node for node, attrs in sim.node_attrs.items() if attrs["state"] == S]
    if susceptible_nodes:
        node_to_infect = random.choice(susceptible_nodes)
        sim.node_attrs[node_to_infect]["state"] = I
        sim.node_attrs[node_to_infect]["quarantine_timer"] = int(quarantine_delay_base * (1 + malware_stealth))
        sim.event_log.append(f"Time {sim.time_step}: ☢️ Malicious file opened on Node {node_to_infect}, which is now Infected!")
    else:
        sim.event_log.append(f"Time {sim.time_step}: File drop failed. No susceptible nodes left to infect.")
    sim.history[-1] = sim.snapshot()
    return sim

# --- Streamlit User Interface ---

st.set_page_config(layout="wide")
st.title("🛡️ Advanced Malware Spread Simulator")

# --- Initialize Session State ---
if 'analyzed_attrs' not in st.session_state:
    st.session_state.analyzed_attrs = None

# --- Sidebar for Simulation Controls ---
with st.sidebar:
    st.header("Simulation Setup")
    topo = st.selectbox("Network Topology", ["Random", "Scale-free"])
    n = st.slider("Number of Nodes", 10, 500, 50)
    inf = st.slider("Initially Infected Nodes", 1, 20, 2)
    seed = st.number_input("Random Seed", 0, 999999, 42)

    with st.expander("Node Attribute Ranges"):
        vuln_range = st.slider("Node Vulnerability", 0.0, 1.0, (0.2, 0.7), 0.01)
        cpu_speed_range = st.slider("Node CPU Speed (e.g., 1.0 = avg)", 0.5, 2.0, (0.8, 1.5), 0.01)
        patch_delay_base = st.slider("Base Patch Delay (steps for avg CPU)", 1, 50, 20)

    with st.expander("Network & Admin Attributes"):
        transmission_delay_range = st.slider("Transmission Delay Range (steps)", 0, 10, (1, 3))
        quarantine_delay_base = st.slider("Base Quarantine Delay (steps)", 1, 50, 10)

    # --- NEW: File Analysis and Action Section ---
    st.markdown("---")
    st.header("Interactive Events")
    uploaded_file = st.file_uploader("Upload a file to analyze as malware")

    if uploaded_file:
        st.session_state.analyzed_attrs = analyze_file_to_get_attributes(uploaded_file)
        st.info(f"File '{uploaded_file.name}' analyzed.")
    
    # Use analyzed attributes if available, otherwise use sliders
    use_analyzed_attrs = st.session_state.analyzed_attrs is not None
    
    with st.expander("Malware Attributes", expanded=True):
        if use_analyzed_attrs:
            analyzed = st.session_state.analyzed_attrs
            st.metric("Analyzed Malware Strength", analyzed['strength'])
            st.metric("Analyzed Malware Stealth", analyzed['stealth'])
            malware_strength = analyzed['strength']
            malware_stealth = analyzed['stealth']
        else:
            malware_strength = st.slider("Malware Strength (Attack Power)", 0.0, 1.0, 0.6, 0.01)
            malware_stealth = st.slider("Malware Stealth (Detection Evasion)", 0.0, 1.0, 0.2, 0.01)

    if uploaded_file:
        if st.button("Simulate File Drop & Infect"):
            sim = st.session_state.sim
            sim = simulate_file_drop(sim, quarantine_delay_base, malware_stealth)
            st.session_state.sim = sim
            # Clear the file and analysis after use to re-enable sliders
            st.session_state.analyzed_attrs = None
            st.rerun()

# --- Simulation Initialization and Execution ---
if topo == "Random": G = nx.erdos_renyi_graph(n, 0.1, seed=seed)
else: G = nx.barabasi_albert_graph(n, 2, seed=seed)

if "sim" not in st.session_state or st.sidebar.button("Reset Simulation", type="primary"):
    sim = Simulation(G=G)
    sim.reset(inf, seed, vuln_range, cpu_speed_range, patch_delay_base, quarantine_delay_base, transmission_delay_range)
    st.session_state.sim = sim
    st.session_state.analyzed_attrs = None # Clear analysis on reset
    st.rerun()
else:
    sim = st.session_state.sim

if st.sidebar.button("Step"):
    sim = step(sim, malware_strength, malware_stealth, quarantine_delay_base)
    st.session_state.sim = sim

# --- Display Results ---
st.header(f"Results at Time Step: {sim.time_step}")
st.line_chart(pd.DataFrame(sim.history).set_index("t"))
tab1, tab2, tab3 = st.tabs(["Node States", "Transmissions", "Event Log"])
with tab1:
    st.subheader("Current State of All Nodes")
    df_data = []
    for node, attrs in sim.node_attrs.items():
        row = {"Node": node, "State": attrs["state"], "Vulnerability": f"{attrs['vulnerability']:.2f}", "CPU Speed": f"{attrs['cpu_speed']:.2f}x"}
        if attrs['state'] == S: row['Time to Patch'] = attrs['patch_timer']
        if attrs['state'] == I: row['Time to Quarantine'] = attrs['quarantine_timer']
        df_data.append(row)
    st.dataframe(pd.DataFrame(df_data), use_container_width=True)
with tab2:
    st.subheader("Active Malware Transmissions")
    if sim.transmissions: st.dataframe(pd.DataFrame(sim.transmissions), use_container_width=True)
    else: st.info("No malware is currently in transit across the network.")
with tab3:
    st.subheader("Simulation Event Log")
    for log in reversed(sim.event_log): st.info(log)

