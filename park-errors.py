from requests_cache import CachedSession
from datetime import timedelta

# Cached session to avoid redundant API calls
session = CachedSession("newparks_cache", expire_after=timedelta(days=1))

# Leaderboard URL template
LEADERBOARD_URL = "https://api.pota.app/park/leaderboard/{reference}?count=1"

# Results list
inconsistent_parks = []

# Fetch list of programs
programs = session.get("https://api.pota.app/programs").json()
print(f"Found {len(programs)} POTA programs")

# For each program, fetch parks
for program in programs:
    prefix = program["programPrefix"]
    name = program["programName"]
    parks_url = f"https://api.pota.app/program/parks/{prefix}"
    parks = session.get(parks_url).json()
    print(f"  → {name} ({prefix}): {len(parks)} parks")

    for park in parks:
        if park["activations"] == 0:
            ref = park["reference"]
            leaderboard_url = LEADERBOARD_URL.format(reference=ref)
            leaderboard = session.get(leaderboard_url).json()

            if leaderboard.get("activations"):  # If not empty, there's a data mismatch
                print(f"    ❌ {ref} | {park['name']} | says 0 activations but leaderboard is NOT empty")
                inconsistent_parks.append({
                    "reference": ref,
                    "name": park["name"],
                    "country": name,
                    "activation_count": park["activations"]
                })

# Write results to file
output_file = "inconsistent_parks.txt"
with open(output_file, "w", encoding="utf-8") as f:
    for park in inconsistent_parks:
        f.write(f"{park['reference']} | {park['name']} | {park['country']} | Reported Activations: {park['activation_count']}\n")

print(f"\n✅ Done. {len(inconsistent_parks)} inconsistent parks found. Written to {output_file}")
