# BOT'S INFO ========================================
CLIENT_ID = 280150025873522688
CLIENT_SECRET = '8oSQ71s4H9vKNODjaL2XypmurtIjXTXD'
CLIENT_USERNAME = 'MikkiBot#0184'
CLIENT_TOKEN = 'MjgwMTUwMDI1ODczNTIyNjg4.C4FNxQ.yX2vyTDktFFbqBWeGT8yYIKamfw'
# ===================================================

# SMUG IMAGES INITIALIZATION ========================
import os

SMUG_LIST = []
for path, subdirs, files in os.walk(r'images/smug'):
    for filename in files:
        SMUG_LIST.append(filename)

SMUG_LIST_SIZE = len(SMUG_LIST)
print(SMUG_LIST_SIZE)
# ===================================================

