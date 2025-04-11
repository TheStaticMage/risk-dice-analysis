#!/usr/bin/env python3

from scipy.stats import norm

# Calculate the p-value

z_score = -9.70909090909

p_value = norm.cdf(z_score)

# Print the p-value

print("p-value:", p_value)