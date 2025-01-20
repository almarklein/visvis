import os
import sys

if __name__ == "__main__":

    sys.path.insert(0, os.path.abspath(os.path.join(__file__, "..", "..", "..")))

    import ssdf

    # Load from file
    s1 = ssdf.load('test1.ssdf')

    # Write to string and read back
    tmp = ssdf.saves(s1)
    s2 = ssdf.loads(tmp)

    # Print, manually inspection required to see whether it matches the test file
    print(s2)
