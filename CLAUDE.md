## Python Environment

- Always use `uv` for Python package management (not pip directly)
- Always use `uv` for running Python scripts. No exceptions.
- Virtual environment: `.venv` in project root
- Activate before running Python: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux)
- Install packages with: `uv pip install <package>`
- Required packages: pandas, openpyxl, seaborn, matplotlib, jupyter

## Chart Style

When creating charts with matplotlib/seaborn, always apply this configuration at the start of the script:

```python
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Inter', 'Helvetica Neue', 'Arial', 'sans-serif'],
    'font.size': 11,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.linewidth': 0.8,
    'axes.edgecolor': '#333333',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linewidth': 0.5,
    'axes.axisbelow': True,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'figure.dpi': 150,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
})

CHART_COLORS = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#FF9DA6', '#9D755D', '#BAB0AC']
sns.set_palette(CHART_COLORS)
```

## Verification

After setup is complete, verify everything works by running:

```bash
uv run python -c "import pandas; import openpyxl; import seaborn; import matplotlib; print('All packages installed successfully!')"
```
