---
name: address-lookup
description: Look up and verify street addresses using OpenStreetMap Nominatim API. Use when you need to find addresses for locations, businesses, churches, or any venue.
---

# Address Lookup

Find and verify street addresses using OpenStreetMap's Nominatim geocoding service (free, no API key required).

## Quick Lookup

```bash
# Look up a location
curl -s "https://nominatim.openstreetmap.org/search?q=QUERY&format=json" | jq .

# Example: Church in Reston
curl -s "https://nominatim.openstreetmap.org/search?q=Saint+Anne%27s+Church+Reston+Virginia&format=json" | jq '.[] | {name: .display_name}'

# Example: Restaurant in NYC
curl -s "https://nominatim.openstreetmap.org/search?q=Balthazar+Restaurant+New+York&format=json" | jq '.[] | {name: .display_name, lat: .lat, lon: .lon}'
```

## Parse Results

```bash
# Get clean address for top result
curl -s "https://nominatim.openstreetmap.org/search?q=QUERY&format=json" | jq -r '.[] | .display_name' | head -1

# Get coordinates (lat/lon)
curl -s "https://nominatim.openstreetmap.org/search?q=QUERY&format=json" | jq '.[] | {name: .display_name, lat: .lat, lon: .lon}' | head -5
```

## Format for Calendar/Events

Extract the street address and format for calendar events:

```
[Name], [Street Address], [City, State ZIP]
```

Example:
- **Church:** Saint Anne's Episcopal Church, 1700 Wainwright Drive, Reston, VA 20190
- **Restaurant:** Balthazar, 80 Spring Street, New York, NY 10012
- **Venue:** The Ritz-Carlton, 50 Central Park South, New York, NY 10019

## Tips

**Better results with:**
- Include city/state for disambiguation
- Use full names (e.g., "Saint Anne's Episcopal Church" not "St Anns")
- Add context if needed (e.g., "restaurant" or "church")

**Reverse Lookup (address to coordinates):**
```bash
# Get lat/lon for an address
curl -s "https://nominatim.openstreetmap.org/search?q=1700+Wainwright+Drive+Reston+VA&format=json" | jq '.[] | {lat, lon}'
```

## Integration with Calendar

Once you have the full address, add it to Google Calendar events:

```bash
gog calendar create primary \
  --summary "Event Name" \
  --from "2026-04-18T14:00:00-04:00" \
  --to "2026-04-18T22:00:00-04:00" \
  --location "Full Street Address, City, State ZIP"
```

## Common Venues (Reston Area)

- **Saint Anne's Episcopal Church:** 1700 Wainwright Drive, Lake Anne Village, Reston, VA 20190
- **Reston Town Center:** 11900 Market Street, Reston, VA 20190
- **Dulles Expo Center:** 4368 Chantilly Shopping Center, Chantilly, VA 20151

## No API Key Required

Nominatim is free and open-source. Just respect rate limits:
- Keep requests to <1/second
- Add a User-Agent header if making many requests
- See: https://nominatim.org/usage_policy.html
