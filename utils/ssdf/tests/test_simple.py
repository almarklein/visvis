import ssdf

# Load from file
s1 = ssdf.load('test1.ssdf')

# Write to string and read back
tmp = ssdf.saves(s1)
s2 = ssdf.loads(tmp)

# Print, manually inspection required to see whether it matches the test file
print(s2)
