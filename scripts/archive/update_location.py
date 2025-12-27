
import pandas as pd
import re
from pathlib import Path

# --- Constants & Mappings ---

US_STATES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    # Abbr to Abbr
    'AL': 'AL', 'AK': 'AK', 'AZ': 'AZ', 'AR': 'AR', 'CA': 'CA', 'CO': 'CO', 'CT': 'CT', 'DE': 'DE',
    'FL': 'FL', 'GA': 'GA', 'HI': 'HI', 'ID': 'ID', 'IL': 'IL', 'IN': 'IN', 'IA': 'IA', 'KS': 'KS',
    'KY': 'KY', 'LA': 'LA', 'ME': 'ME', 'MD': 'MD', 'MA': 'MA', 'MI': 'MI', 'MN': 'MN', 'MS': 'MS',
    'MO': 'MO', 'MT': 'MT', 'NE': 'NE', 'NV': 'NV', 'NH': 'NH', 'NJ': 'NJ', 'NM': 'NM', 'NY': 'NY',
    'NC': 'NC', 'ND': 'ND', 'OH': 'OH', 'OK': 'OK', 'OR': 'OR', 'PA': 'PA', 'RI': 'RI', 'SC': 'SC',
    'SD': 'SD', 'TN': 'TN', 'TX': 'TX', 'UT': 'UT', 'VT': 'VT', 'VA': 'VA', 'WA': 'WA', 'WV': 'WV',
    'WI': 'WI', 'WY': 'WY', 'DC': 'DC', 'District of Columbia': 'DC'
}

# Known international locations to map to "Abroad"
INTERNATIONAL_LOCATIONS = {
    'Davos', 'Jerusalem', 'Riyadh', 'Vietnam', 'Ossie', 'Hanoi', 'Osaka', 'Biarritz', 
    'London', 'Normandy', 'Shannon', 'Doocastle', 'Tokyo', 'Panmunjom', 'Singapore', 
    'Quebec', 'Hamburg', 'Warsaw', 'Sicily', 'Brussels', 'The Vatican', 'Bethlehem', 
    'Manila', 'Da Nang', 'Seoul', 'Beijing', 'France', 'Germany', 'United Kingdom',
    'Switzerland', 'Poland', 'Italy', 'Japan', 'South Korea', 'China', 'Philippines',
    'Canada', 'Ireland', 'Saudi Arabia', 'Israel', 'Qatar', 'Argentina', 'India'
}

# Specific cleanups
OVERRIDES = {
    'the Rose Garden': 'Washington, DC',
    'the White House': 'Washington, DC',
    'The White House': 'Washington, DC',
    'Bedminster': 'Bedminster, NJ',
    'Mar-a-Lago': 'Palm Beach, FL',
    'Trump Tower': 'New York, NY',
    'Andrews Air Force Base': 'Camp Springs, MD',
    'Joint Base Andrews': 'Camp Springs, MD',
    'Walter Reed': 'Bethesda, MD',
    'Arlington': 'Arlington, VA',
    'Lima': 'Lima, OH',
}

def extract_raw_location(title):
    if not isinstance(title, str):
        return None
    
    # Try to find the LAST " in " to avoid "a Town Hall in..." prefixes
    # We use rsplit to find the last occurrence
    parts = title.rsplit(' in ', 1)
    if len(parts) > 1:
        # Check if there is a " - " after the location
        loc_candidate = parts[1]
        
        # Often suffix is " - Date" or just end of string
        # Regex to split off the suffix
        match = re.search(r'^(.*?)(?: - \w+ \d+, \d{4}|$)', loc_candidate)
        if match:
             return match.group(1).strip().rstrip('.') # Remove trailing dot
        
        # Fallback regex if date format varies
        match = re.search(r'^(.*?)(?: -|$)', loc_candidate)
        if match:
            return match.group(1).strip().rstrip('.')

    return None

def standardize_location(raw_loc):
    if not raw_loc:
        return 'Unknown'
    
    # Normalize whitespaces
    loc = ' '.join(raw_loc.split())
    
    # Check overrides
    for key, val in OVERRIDES.items():
        if key.lower() in loc.lower():
            return val
            
    # Try to parse "Town, State" - PRIORITY 1: US States
    # We do this before International check to catch "Indiana, PA" (contains "India")
    # or "Paris, TX" (contains "Paris").
    if ',' in loc:
        parts = loc.split(',')
        state_part = parts[-1].strip()
        town_part = ', '.join(parts[:-1]).strip()
        
        # Check if state_part is a valid state
        state_code = US_STATES.get(state_part)
        # Try stripping periods
        if not state_code:
             cleaned_state = state_part.replace('.', '')
             state_code = US_STATES.get(cleaned_state)
             
        if state_code:
            return f"{town_part}, {state_code}"
            
    # Check if it contains an international location
    # Use word boundary to avoid "India" matching "Indiana"
    for intl in INTERNATIONAL_LOCATIONS:
        # Regex search for whole word
        if re.search(r'\b' + re.escape(intl) + r'\b', loc):
            return 'Abroad'
            
    # Try exact match on State name alone
    if loc in US_STATES:
        return US_STATES[loc]
        
    # Common US Cities (add more as needed)
    common_cities = {
        'Austin': 'TX', 'Atlanta': 'GA', 'Chicago': 'IL', 'Detroit': 'MI',
        'Milwaukee': 'WI', 'Las Vegas': 'NV', 'Minneapolis': 'MN', 'Phoenix': 'AZ',
        'Pittsburgh': 'PA', 'Philadelphia': 'PA', 'Miami': 'FL', 'Tampa': 'FL',
        'Orlando': 'FL', 'Jacksonville': 'FL', 'Cleveland': 'OH', 'Cincinnati': 'OH',
        'Columbus': 'OH', 'Doral': 'FL', 'West Palm Beach': 'FL', 'Nashville': 'TN',
        'Charlotte': 'NC', 'Raleigh': 'NC', 'Greensboro': 'NC',
        'Houston': 'TX', 'Dallas': 'TX', 'San Antonio': 'TX',
        'Los Angeles': 'CA', 'San Francisco': 'CA', 'San Diego': 'CA',
        'Denver': 'CO', 'Seattle': 'WA', 'Portland': 'OR',
        'Boston': 'MA', 'Baltimore': 'MD', 'St. Louis': 'MO', 'Kansas City': 'MO',
        'Indianapolis': 'IN', 'New Orleans': 'LA', 'Salt Lake City': 'UT',
        'Louisville': 'KY', 'Richmond': 'VA', 'Oklahoma City': 'OK',
        'Tulsa': 'OK', 'El Paso': 'TX', 'Memphis': 'TN',
    }
    
    if loc in common_cities:
        return f"{loc}, {common_cities[loc]}"
        
    # Check if the location is known to be a US city without state (rare in this dataset but could happen)
    # E.g. "Washington" -> "Washington, DC" (Handled in Overrides mostly or implicit)
    if 'Washington' == loc:
        return 'Washington, DC'
    if 'New York City' in loc or 'NYC' in loc:
        return 'New York, NY'
    
    # If we couldn't match a state, and we haven't identified it as Abroad... 
    # it likely is garbage extraction like "Support of His Budget" or "Advance of the Inaugural Lunch".
    # User said "If it is not in the us, just call it 'abroad'", but we should be careful not to label 
    # non-locations as Abroad.
    # Our INTERNATIONAL_LOCATIONS list handles known foreign places.
    # Fallback to Unknown is safer for quality.
    
    return 'Unknown'

def update_speeches_location():
    data_dir = Path("data")
    speeches_path = data_dir / "speeches.parquet"
    
    if not speeches_path.exists():
        print(f"Error: {speeches_path} not found.")
        return

    print(f"Loading {speeches_path}...")
    df = pd.read_parquet(speeches_path)
    
    print("Extracting and standardizing locations...")
    
    # 1. Extract raw
    df['raw_location'] = df['title'].apply(extract_raw_location)
    
    # 2. Standardize
    df['location'] = df['raw_location'].apply(standardize_location)
    
    print("\n--- Standardization Samples ---")
    sample = df[['raw_location', 'location']].drop_duplicates().sample(20)
    print(sample.to_string())
    
    print("\n--- Non-US / Special ---")
    print(df[df['location'] == 'Abroad'][['title', 'location']].head(5).to_string())
    print(df[df['location'] == 'Unknown'][['title', 'location']].head(5).to_string())
    
    print("Saving updated parquet file...")
    # Rename original for safety
    backup_path = data_dir / "speeches_backup.parquet"
    if not backup_path.exists():
        df_old = pd.read_parquet(speeches_path)
        df_old.to_parquet(backup_path)
        print(f"Backup saved to {backup_path}")
    
    # Drop raw_location before saving
    df.drop(columns=['raw_location'], inplace=True)
    
    df.to_parquet(speeches_path)
    print("Done!")

if __name__ == "__main__":
    update_speeches_location()
