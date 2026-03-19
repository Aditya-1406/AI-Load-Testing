import streamlit as st
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from concurrency_test import (
    collect_trial,
    feature_engineering,
    train_regression_model,
    train_failure_classifier,
    anomaly_detection,
    estimate_failure_threshold,
    digital_twin_simulation,
    NUM_TRIALS,
    set_target_api  # ✅ NEW IMPORT
)


st.set_page_config(page_title="AI Load Testing Dashboard", layout="wide")

st.title("🚀 AI-Based Load Testing Dashboard")
st.sidebar.header("⚙️ Controls")


api_url = st.sidebar.text_input(
    "Enter API URL",
    "http://127.0.0.1:8005/notes"
)

max_users = st.sidebar.slider(
    "Max Users",
    min_value=100,
    max_value=10000,
    value=2000,
    step=100
)

run_test = st.sidebar.button("▶️ Run Load Test")

uploaded_file = st.sidebar.file_uploader("Or Upload CSV", type=["csv"])

async def run_full_pipeline():

    all_trials = []

    progress = st.progress(0)
    status = st.empty()

    for trial in range(1, NUM_TRIALS + 1):

        status.text(f"Running Trial {trial}...")

        df_trial = await collect_trial(trial)
        all_trials.append(df_trial)

        progress.progress(trial / NUM_TRIALS)

    df = pd.concat(all_trials, ignore_index=True)

    df = feature_engineering(df)

    df, model, scaler = train_regression_model(df)

    df = train_failure_classifier(df)

    df = anomaly_detection(df)

    estimate_failure_threshold(df)

    return df, model, scaler

df = None
model = None
scaler = None

if run_test:
    st.info("⏳ Running Load Test... This may take time")

    set_target_api(api_url)
    
    import concurrency_test
    concurrency_test.MAX_USERS = max_users

    df, model, scaler = asyncio.run(run_full_pipeline())

    df.to_csv("ai_load_testing_results.csv", index=False)

    st.success("✅ Load Testing Completed")

elif uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ CSV Loaded Successfully")



if df is not None:

    st.subheader("📊 Dataset")
    st.dataframe(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Latency", f"{df['latency'].mean():.2f} ms")
    col2.metric("Error Rate", f"{df['error_rate'].mean():.3f}")
    col3.metric("Max Users", int(df["users"].max()))
    col4.metric("Max CPU", f"{df['cpu_usage'].max():.1f}%")

    st.subheader("📈 Latency vs Users")

    df_sorted = df.sort_values(by="users")

    fig, ax = plt.subplots(figsize=(8,5))
    ax.scatter(df_sorted["users"], df_sorted["latency"])
    ax.plot(df_sorted["users"], df_sorted["latency"], linestyle="--")

    if "latency_ci_low" in df.columns:
        ax.fill_between(
            df_sorted["users"],
            df_sorted["latency_ci_low"],
            df_sorted["latency_ci_high"],
            alpha=0.2
        )

    ax.set_xlabel("Users")
    ax.set_ylabel("Latency")
    st.pyplot(fig)

  
    if "predicted_latency" in df.columns:

        st.subheader("🎯 Model Accuracy")

        fig, ax = plt.subplots()
        ax.scatter(df["latency"], df["predicted_latency"])

        min_val = min(df["latency"].min(), df["predicted_latency"].min())
        max_val = max(df["latency"].max(), df["predicted_latency"].max())

        ax.plot([min_val, max_val], [min_val, max_val], linestyle="--")

        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")

        st.pyplot(fig)

 
    if "failure_probability" in df.columns:

        st.subheader("⚠️ Failure Probability")

        fig, ax = plt.subplots()
        ax.plot(df_sorted["users"], df_sorted["failure_probability"])
        ax.axhline(y=0.8, linestyle="--")

        critical = df[df["failure_probability"] > 0.8]

        if not critical.empty:
            ax.scatter(critical["users"], critical["failure_probability"], marker="x")

        st.pyplot(fig)

 
    if "anomaly" in df.columns:

        st.subheader("🚨 Anomaly Detection")

        normal = df[df["anomaly"] == 1]
        anomaly = df[df["anomaly"] == -1]

        fig, ax = plt.subplots()
        ax.scatter(normal["users"], normal["latency"], label="Normal")
        ax.scatter(anomaly["users"], anomaly["latency"], marker="x", label="Anomaly")
        ax.legend()

        st.pyplot(fig)


    if model is not None and scaler is not None:

        st.subheader("🔮 Digital Twin Simulation")

        digital_twin_simulation(model, scaler)

        fig = plt.gcf()
        st.pyplot(fig)
        plt.clf()

    st.subheader("🧠 AI Insights")

    if "failure_probability" in df.columns:
        critical = df[df["failure_probability"] > 0.8]

        if not critical.empty:
            st.error(f"⚠️ System may fail at ~{int(critical['users'].iloc[0])} users")
        else:
            st.success("✅ System stable under tested load")
