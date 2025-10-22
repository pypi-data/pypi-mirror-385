from mcdplib import *

print(os.listdir("."))

dp = Datapack(PackInformation(
    min_format=(0, 0),
    max_format=1,
    description="bebebe"
))
dp.load("data")
dp.build({})
dp.write(".out")