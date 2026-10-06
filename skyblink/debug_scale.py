import numpy as np
import sys
sys.path.append("d:/Space App Challenge/skyblink")
from pipeline.skyblink_pipeline.core.run import background_scale_diff

shape = (100, 100)
img_A = np.full(shape, 10.0)
img_B = np.full(shape, 10.0)
img_A[50, 50] = 1000.0 + 10.0
img_B[50, 50] = (1000.0 * 2.5) + 10.0
mask = np.ones(shape, dtype=bool)
var = np.ones(shape)

bg_A = fit_background(img_A, mask)
sub_A = img_A - bg_A
perc = np.percentile(sub_A[mask], 95)
bright_mask = (sub_A > perc) & mask
print("Max sub_A:", np.max(sub_A))
print("95th percentile:", perc)
print("Sum bright_mask:", np.sum(bright_mask))
D, var_D, scale, fit_bg_A, fit_bg_B = background_scale_diff(img_A, var, img_B, var, mask)
print("Scale:", scale)
