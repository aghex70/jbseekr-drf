from jbseekr.apps.seeker import tasks

print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
print(f"@@@@@@@@@@@@@@@@@@")
tasks.generate_offers.apply_async(kwargs={}, countdown=0)
