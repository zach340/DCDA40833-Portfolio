import pandas as pd
import folium
import requests
import time

# Your Mapbox API key
MAPBOX_API_KEY = "pk.eyJ1IjoiemFjYW1wYmVsbCIsImEiOiJjbWx0cGk0MGYwMnJxM2RvbTd4ZXVjam16In0.OquKlnWfFbaFrMZaczfJpg"

# Read the CSV file
locations = pd.read_csv(r"C:\Users\Zachc\OneDrive\Documents\Hometown_locations.csv")

# Function to geocode addresses using Mapbox
def geocode_address(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {
        'access_token': MAPBOX_API_KEY,
        'limit': 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            coordinates = data['features'][0]['center']
            return coordinates[1], coordinates[0]  # Returns (latitude, longitude)
    return None, None

# Add latitude and longitude columns
locations['latitude'] = None
locations['longitude'] = None

# Geocode each address
for idx, row in locations.iterrows():
    address = row['Address']  # Change 'address' to your actual column name
    print(f"Geocoding: {address}")
    lat, lon = geocode_address(address)
    locations.at[idx, 'latitude'] = lat
    locations.at[idx, 'longitude'] = lon
    time.sleep(0.2)  # Rate limiting

# Save geocoded data
locations.to_csv(r"C:\Users\Zachc\OneDrive\Documents\Hometown_locations_geocoded.csv", index=False)

# Create a folium map with custom Mapbox basemap
valid_locations = locations.dropna(subset=['latitude', 'longitude'])

if not valid_locations.empty:
    center_lat = valid_locations['latitude'].mean()
    center_lon = valid_locations['longitude'].mean()
    
    # Use @2x for retina/high-DPI tiles which makes text appear larger and crisper
    mapbox_tile_url = f"https://api.mapbox.com/styles/v1/zacampbell/cmm9qop36000m01qnh4waedjx/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_API_KEY}"
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,  # Increased from 12 for larger text
        tiles=mapbox_tile_url,
        attr='Mapbox'
    )
    
    for idx, row in valid_locations.iterrows():
        location_type = row.get('Type', '').lower()
        
        if 'park' in location_type or 'recreational' in location_type:
            style = {'color': 'red', 'icon': 'tree', 'prefix': 'fa'}
        elif 'restaurant' in location_type:
            style = {'color': 'gray', 'icon': 'utensils', 'prefix': 'fa'}
        elif 'school' in location_type:
            style = {'color': 'black', 'icon': 'graduation-cap', 'prefix': 'fa'}
        else:
            style = {'color': 'blue', 'icon': 'info-sign', 'prefix': 'glyphicon'}
        
        # Create HTML for popup with name, description, and image
        popup_html = f"""
        <div style="width: 300px; font-family: Arial;">
            <h4 style="margin-top: 0;">{row.get('Name', 'Location')}</h4>
            <p><strong>Description:</strong><br>{row.get('Discription', 'No description available')}</p>
            {f'<img src="{row.get("Image_URL")}" alt="Location image" style="width: 100%; max-width: 300px; height: auto; margin-top: 10px;">' if pd.notna(row.get('Image_URL')) else ''}
        </div>
        """
        
        iframe = folium.IFrame(html=popup_html, width=320, height=400)
        popup = folium.Popup(iframe, max_width=350)
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup,
            tooltip=row.get('Name', 'Location'),
            icon=folium.Icon(
                color=style['color'],
                icon=style['icon'],
                prefix=style['prefix']
            )
        ).add_to(m)
    
    m.save("hometown_map.html")
    print("Map saved to hometown_map.html")
else:
    print("No valid coordinates to map")