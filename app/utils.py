# app/utils.py
import matplotlib.pyplot as plt
from pathlib import Path
import uuid

def make_sample_chart(numbers, labels=None):
    # creates and saves a chart, returns path
    fn = f"static/chart-{uuid.uuid4().hex}.png"
    Path("static").mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.plot(numbers)
    plt.title("Sample Chart")
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig(fn)
    plt.close()
    return fn