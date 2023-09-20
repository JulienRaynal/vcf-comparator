import matplotlib.pyplot as plt
from matplotlib_venn import venn3

venn3(subsets=(38, 24, 15, 26, 5, 0, 15), set_labels = ("P15", "P30", "P50"))
plt.show()
