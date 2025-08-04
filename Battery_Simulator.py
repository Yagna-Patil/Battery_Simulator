import streamlit as st
import random
import time
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
import datetime

# ------------------ Streamlit UI Config ------------------
st.set_page_config(page_title="🔋 Battery Simulator", layout="wide")
st.title("🔋 Interactive Battery Simulation Dashboard")
st.sidebar.header("⚙️ Configuration")

# ------------------ Cell Configuration ------------------
number_of_cells = st.sidebar.number_input("Enter number of cells", min_value=1, max_value=10, value=3)

cell_types = []
for i in range(number_of_cells):
    cell_type = st.sidebar.selectbox(f"Select type for Cell {i+1}", ["lfp", "nmc"], key=f"cell_{i}")
    cell_types.append(cell_type)

# ------------------ Generate Cells Data ------------------
cells_data = {}
for idx, cell_type in enumerate(cell_types, start=1):
    cell_key = f"Cell {idx} ({cell_type})"
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    current = round(random.uniform(0.5, 2.0), 2)
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)
    cells_data[cell_key] = {
        "voltage": voltage,
        "current": current,
        "temp": temp,
        "capacity": capacity,
        "min_voltage": min_voltage,
        "max_voltage": max_voltage
    }

# ------------------ Dashboard Display ------------------
st.subheader("🔋 Battery Dashboard")
cols = st.columns(number_of_cells)
selected_cell = None

for idx, (key, data) in enumerate(cells_data.items()):
    with cols[idx]:
        if st.button(f"{key}", key=f"btn_{idx}"):
            selected_cell = key
        charge_percent = (data["voltage"] - data["min_voltage"]) / (data["max_voltage"] - data["min_voltage"]) * 100
        st.progress(charge_percent / 100, f"{charge_percent:.1f}%")

# ------------------ Cell Detail Sidebar ------------------
if selected_cell:
    st.sidebar.subheader(f"🔍 Details of {selected_cell}")
    details = cells_data[selected_cell]
    for k, v in details.items():
        st.sidebar.write(f"*{k}*: {v}")

# ------------------ Task Simulation ------------------
st.subheader("🛠️ Task Simulation")
task_types = ["CC_CV", "IDLE", "CC_CD"]
num_tasks = st.number_input("Enter number of tasks", min_value=1, max_value=5, value=2)

task_list = []
for i in range(num_tasks):
    st.markdown(f"### Task {i+1}")
    task_type = st.selectbox(f"Select task type for Task {i+1}", task_types, key=f"task_type_{i}")
    task = {"task_type": task_type}

    if task_type == "CC_CV":
        task["cc_cp"] = st.text_input(f"CC/CP value for Task {i+1} (e.g. '5A')", key=f"cccv_{i}")
        task["cv_voltage"] = st.number_input("CV Voltage (V)", key=f"cv_{i}")
        task["current"] = st.number_input("Current (A)", key=f"cur_{i}")
        task["capacity"] = st.number_input("Capacity", key=f"cap_{i}")
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"time_{i}")
    elif task_type == "IDLE":
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"idle_time_{i}")
    elif task_type == "CC_CD":
        task["cc_cp"] = st.text_input(f"CC/CP value for Task {i+1} (e.g. '5A')", key=f"cccd_{i}")
        task["voltage"] = st.number_input("Voltage (V)", key=f"volt_{i}")
        task["capacity"] = st.number_input("Capacity", key=f"cap_cd_{i}")
        task["time_seconds"] = st.slider("Duration (s)", 5, 60, 10, key=f"cd_time_{i}")

    task_list.append(task)

# ------------------ Simulation Trigger ------------------
if st.button("▶️ Start Simulation"):
    st.success("Running simulation...")

    voltages, currents, temps, times = [], [], [], []
    progress_bar = st.progress(0)
    graph_placeholder = st.empty()
    start_time = datetime.datetime.now()

    for t in range(100):
        voltage = round(random.uniform(3.0, 4.2), 2)
        current = round(random.uniform(0.5, 5.0), 2)
        temp = round(random.uniform(25, 45), 1)

        voltages.append(voltage)
        currents.append(current)
        temps.append(temp)
        times.append(t)
        progress_bar.progress((t + 1) / 100)
        time.sleep(0.05)

        with graph_placeholder.container():
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
            ax1.plot(times, voltages, 'g-', label="Voltage (V)")
            ax2.plot(times, currents, 'b--', label="Current (A)")
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Voltage (V)", color="green")
            ax2.set_ylabel("Current (A)", color="blue")
            fig.suptitle("🔌 Real‑Time Voltage and Current vs Time")
            ax1.tick_params(axis='y', labelcolor='green')
            ax2.tick_params(axis='y', labelcolor='blue')
            fig.tight_layout()
            st.pyplot(fig)

    st.success("✅ Simulation Complete!")

    df = pd.DataFrame({
        "Time (s)": times,
        "Voltage (V)": voltages,
        "Current (A)": currents,
        "Temperature (°C)": temps
    })
    st.subheader("📄 Export Graph Data")
    st.dataframe(df.head())
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(label="📥 Download Simple CSV", data=csv_buffer.getvalue(), file_name="battery_simulation_data.csv", mime="text/csv")

    def generate_simulation_csv(voltages, temps, currents, start_time, jump_events):
        test_data_rows = []
        for i, (v, t, c) in enumerate(zip(voltages, temps, currents)):
            sample_id = i + 1
            sampling_time = f"{(i*2)//60:02d}:{(i*2)%60:02d}"
            actual_time = (start_time + datetime.timedelta(seconds=i*2)).strftime("%H:%M:%S")
            capacity = round(c * 2 / 3600, 6)
            energy = round(capacity * v, 6)
            step_type = "Constant Current" if i < len(voltages) // 2 else "Rest"
            test_data_rows.append([
                sample_id, sampling_time, "", actual_time, v, c,
                capacity, energy, step_type, 1, i+1, 0, t
            ])
        test_df = pd.DataFrame(test_data_rows, columns=[
            "Sample ID", "Sampling", "Termination", "Actual Time", "Voltage (V)",
            "Current (A)", "Capacity (Ah)", "Energy (Wh)", "Step Type",
            "Cycle Count", "Step Num", "DC Resist", "Temperature (°C)"
        ])
        stats_df = pd.DataFrame([[1, 0.056245, 0, 0.056245, 0.042359,
                                   "00:40.0", "00:00.0", "00:30.0", "00:30.0", 75.31297,
                                   100, 3.207877, 3.207877, max(temps), 15.6]],
                                 columns=[
                                   "Cycle Num", "CC Charge", "CV Charge", "Total Charge", "Total Disch",
                                   "CC Charge Time", "CV Charge Time", "CC Disch Time", "Total Disch Time",
                                   "Efficiency (%)", "Capacity (%)", "Avg Disch Volt", "Median Volt",
                                   "Max Temp", "DC Resistance (mΩ)"
                                 ])
        op_log = [[e["timestamp"], e["sample_id"], e["event"]] for e in jump_events]
        op_log_df = pd.DataFrame(op_log, columns=["Timestamp", "Sample ID", "Event Type"])
        proc_df = pd.DataFrame([["CC‑CV Charge", "Constant Voltage", 5, 3.65, 3.65,
                                 0.05, 6, "00:40.0", 0.03, 0, 1]],
                               columns=["Step Type", "Constant Type", "Voltage Limit", "Current Limit",
                                        "Capacity Limit", "Time Limit", "Temp Limit", "Delta V Limit",
                                        "Target Cap", "Step Num", "Jump Count"])
        output = StringIO()
        output.write("### Test Data ###\n")
        test_df.to_csv(output, index=False)
        output.write("\n### Cycle Statistics ###\n")
        stats_df.to_csv(output, index=False)
        output.write("\n### Operation Log ###\n")
        op_log_df.to_csv(output, index=False)
        output.write("\n### Process Information ###\n")
        proc_df.to_csv(output, index=False)
        return output.getvalue()

    jump_events = [
        {"timestamp": "19:31.7", "sample_id": 3, "event": "Step jumped due to time limit"},
    ]
    detailed_csv = generate_simulation_csv(voltages, temps, currents, start_time, jump_events)
    st.download_button(label="📥 Download Detailed Report CSV", data=detailed_csv, file_name="battery_detailed_report.csv", mime="text/csv")
