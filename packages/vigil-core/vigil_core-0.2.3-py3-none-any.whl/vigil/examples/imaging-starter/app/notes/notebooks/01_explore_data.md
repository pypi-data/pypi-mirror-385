# Data Exploration

```python
import pandas as pd
# Load your sample data
df = pd.read_csv("app/data/samples/data.csv")
df.head()
```

```python
# Basic statistics
df.describe()
```

```python
# Visualize value distribution
import matplotlib.pyplot as plt
df["value"].hist(bins=10)
plt.xlabel("Value")
plt.ylabel("Count")
plt.title("Value Distribution")
plt.show()
```
