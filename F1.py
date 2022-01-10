import numpy as np
from sklearn.metrics import f1_score

# Totaled Detection Results
TP = int(input("\n True Positives: "))
FN = int(input(" False Negatives: "))
FP = int(input(" False Positives: "))
TN = int(input(" True Negatives: "))

# Define Actual Classes
extremes = np.repeat([1, 0], repeats=[TP+FN, FP+TN])

# Define Predicted Results
result = np.repeat([1, 0, 1, 0], repeats=[TP, FN, FP, TN])

# Calculate F1 score
f1 = f1_score(extremes, result)

print("\n F1 Score: " + str(f1))

import bcrypt
import time as t

password = "AaronJoshuaSenar"

b1 = bytes(password, encoding='utf-8')

dur = t.perf_counter_ns()

hash1 = bcrypt.hashpw(b1, bcrypt.gensalt(rounds=12))

dur = float(delay.perf_counter_ns() - dur)

print("Time Elapsed: " + str(start // 1000000) + "milliseconds")
print(hash1)

password = bytes(password, encoding='utf-8')


if bcrypt.checkpw(password, hash1):
	print("Hash Success")
else:
	print("Hash Fail")





