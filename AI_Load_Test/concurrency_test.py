import asyncio
import aiohttp
import time
import numpy as np
import pandas as pd
import random
import psutil
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, VotingRegressor, IsolationForest
from sklearn.linear_model import LogisticRegression
from scipy import stats

np.random.seed(42)
random.seed(42)


BASE_URL = ""
NOTES_URL = ""

START_USERS = 1
MAX_USERS = 2000

TIMEOUT = 5
BATCH_SIZE = 500

NUM_TRIALS = 5
KFOLD_SPLITS = 5


def set_target_api(url):
    global BASE_URL, NOTES_URL
    BASE_URL = url
    NOTES_URL = url


def get_adaptive_step(latency, error_rate):
    if error_rate > 0.2 or latency > 2000:
        return 50
    elif latency > 1000:
        return 100
    else:
        return 200

def get_system_metrics():
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    return cpu, memory


def latency_confidence_interval(latencies):

    if len(latencies) < 2:
        return np.nan, np.nan

    mean = np.mean(latencies)
    sem = stats.sem(latencies)

    if sem == 0:
        return mean, mean

    ci_low, ci_high = stats.t.interval(
        0.95,
        len(latencies)-1,
        loc=mean,
        scale=sem
    )

    return ci_low, ci_high


async def send_request(session):

    start = time.perf_counter()

    try:
        async with session.get(NOTES_URL) as response:
            await response.text()
            error = 0 if response.status == 200 else 1
    except Exception:
        error = 1

    latency = (time.perf_counter() - start) * 1000

    return latency, error

async def run_load(users):

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    connector = aiohttp.TCPConnector(limit=BATCH_SIZE)

    start_total = time.perf_counter()

    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout
    ) as session:

        tasks = [send_request(session) for _ in range(users)]
        results = await asyncio.gather(*tasks)

    total_duration = time.perf_counter() - start_total

    latencies, errors = zip(*results)

    latencies = np.array(latencies)
    errors = np.array(errors)

    avg_latency = np.mean(latencies)
    p95_latency = np.percentile(latencies, 95)

    error_rate = np.mean(errors)
    throughput = users / (total_duration + 1e-9)

    ci_low, ci_high = latency_confidence_interval(latencies)
    cpu_usage, memory_usage = get_system_metrics()

    return (
        avg_latency,
        p95_latency,
        error_rate,
        throughput,
        cpu_usage,
        memory_usage,
        ci_low,
        ci_high
    )


async def collect_trial(trial_id):

    print(f"\n🔬 Trial {trial_id} Starting...\n")

    records = []
    users = START_USERS

    while users <= MAX_USERS:

        (
            avg_latency,
            p95_latency,
            error_rate,
            throughput,
            cpu_usage,
            memory_usage,
            ci_low,
            ci_high
        ) = await run_load(users)

        print(
            f"Trial {trial_id} | Users={users:4} | "
            f"Avg={avg_latency:8.2f}ms | "
            f"P95={p95_latency:8.2f}ms | "
            f"Err={error_rate:.3f}"
        )

        records.append([
            trial_id,
            users,
            avg_latency,
            p95_latency,
            error_rate,
            throughput,
            cpu_usage,
            memory_usage,
            ci_low,
            ci_high
        ])

        step = get_adaptive_step(avg_latency, error_rate)
        users += step

    df = pd.DataFrame(records, columns=[
        "trial",
        "users",
        "latency",
        "p95_latency",
        "error_rate",
        "throughput",
        "cpu_usage",
        "memory_usage",
        "latency_ci_low",
        "latency_ci_high"
    ])

    return df

def feature_engineering(df):

    df["load_factor"] = df["users"] / MAX_USERS
    df["error_pressure"] = df["error_rate"] * df["latency"]
    df["efficiency"] = df["throughput"] / (df["latency"] + 1)
    df["stress_index"] = df["users"] * df["error_rate"]
    df["latency_volatility"] = df["p95_latency"] - df["latency"]
    df["resource_pressure"] = df["cpu_usage"] * df["memory_usage"]

    return df

def train_regression_model(df):

    features = [
        "users","error_rate","throughput","cpu_usage","memory_usage",
        "load_factor","error_pressure","efficiency","stress_index",
        "latency_volatility","resource_pressure"
    ]

    X = df[features].values
    y = df["latency"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kf = KFold(n_splits=KFOLD_SPLITS, shuffle=True, random_state=42)

    for train_idx, test_idx in kf.split(X_scaled):
        model = VotingRegressor([
            ("gb", GradientBoostingRegressor(n_estimators=300)),
            ("rf", RandomForestRegressor(n_estimators=300))
        ])
        model.fit(X_scaled[train_idx], y[train_idx])

    final_model = model
    final_model.fit(X_scaled, y)

    df["predicted_latency"] = final_model.predict(X_scaled)

    return df, final_model, scaler

def train_failure_classifier(df):

    df["failure_label"] = (
        (df["latency"] > df["latency"].quantile(0.85)) |
        (df["error_rate"] > 0.2)
    ).astype(int)

    features = [
        "users","error_rate","throughput","cpu_usage","memory_usage",
        "load_factor","error_pressure","efficiency","stress_index",
        "latency_volatility","resource_pressure"
    ]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[features])

    clf = LogisticRegression(max_iter=500)
    clf.fit(X_scaled, df["failure_label"])

    df["failure_probability"] = clf.predict_proba(X_scaled)[:,1]

    return df

def anomaly_detection(df):

    iso = IsolationForest(contamination=0.1)

    df["anomaly"] = iso.fit_predict(
        df[["latency","error_rate","throughput","cpu_usage","memory_usage"]]
    )

    return df

def estimate_failure_threshold(df):
    """
    Estimate the user load where system starts failing
    based on failure probability.
    """

    if "failure_probability" not in df.columns:
        return None

    critical = df[df["failure_probability"] > 0.8]

    if not critical.empty:
        threshold = int(critical["users"].iloc[0])
        print(f"⚠️ Estimated Failure Threshold: ~{threshold} users")
        return threshold

    print("✅ System stable under tested load")
    return None

def digital_twin_simulation(model, scaler):

    simulated_users = np.arange(100, 10001, 200)

    fake = pd.DataFrame({
        "users": simulated_users,
        "error_rate": np.linspace(0,1,len(simulated_users)),
        "throughput": np.linspace(100,10,len(simulated_users)),
        "cpu_usage": np.linspace(20,100,len(simulated_users)),
        "memory_usage": np.linspace(30,90,len(simulated_users))
    })

    fake["load_factor"] = fake["users"] / MAX_USERS
    fake["error_pressure"] = fake["error_rate"] * 1000
    fake["efficiency"] = fake["throughput"] / 100
    fake["stress_index"] = fake["users"] * fake["error_rate"]
    fake["latency_volatility"] = 100
    fake["resource_pressure"] = fake["cpu_usage"] * fake["memory_usage"]

    X_scaled = scaler.transform(fake.values)
    pred = model.predict(X_scaled)

    plt.figure()
    plt.plot(simulated_users, pred)
    plt.title("Digital Twin Simulation")
    plt.grid(True)

async def main():

    api = input("Enter API URL: ")
    set_target_api(api)

    global MAX_USERS
    max_users = input("Max users (default 2000): ")
    if max_users.strip():
        MAX_USERS = int(max_users)

    all_trials = []

    for trial in range(1, NUM_TRIALS+1):
        df_trial = await collect_trial(trial)
        all_trials.append(df_trial)

    df = pd.concat(all_trials, ignore_index=True)

    df = feature_engineering(df)
    df, model, scaler = train_regression_model(df)
    df = train_failure_classifier(df)
    df = anomaly_detection(df)

    df.to_csv("ai_load_testing_results.csv", index=False)

    print("\n✅ COMPLETED")


if __name__ == "__main__":
    asyncio.run(main())
