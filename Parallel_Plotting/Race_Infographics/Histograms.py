import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
file_path = '2023_RaceInfographicsExtract.xlsx'
df = pd.read_excel(file_path)

# List of metrics to plot
metrics = ["Traction", "Tyre Stress", "Asphalt Grip", "Braking", 
           "Asphalt Abrasion", "Lateral", "Track Evolution", "Downforce"]

# Track to highlight
highlight_circuit = "Bahrain"  # Example, you can change this to any track

# Create a figure with 2x4 subplots
fig, axes = plt.subplots(2, 4, figsize=(18, 10))
axes = axes.flatten()

# Loop over the metrics to create a histogram for each
for i, metric in enumerate(metrics):
    ax = axes[i]
    
    # Extract the data for the current metric
    metric_values = df[metric].astype(int)
    
    # Plot the histogram
    counts, bins, patches = ax.hist(metric_values, bins=range(1, 7), align='left', edgecolor='black', alpha=0.7)
    
    # Highlight the bar corresponding to the selected track
    highlight_value = int(df[df['Circuit'] == highlight_circuit][metric])
    for patch, bin_value in zip(patches, bins):
        if bin_value == highlight_value:
            patch.set_facecolor('red')  # Highlight with red color

    # Set plot titles and labels
    ax.set_title(metric)
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.set_xticks(range(1, 6))

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()
