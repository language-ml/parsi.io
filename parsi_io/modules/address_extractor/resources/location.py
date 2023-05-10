from geopy.geocoders import Nominatim
import geocoder

class LatLong():
    def __init__(self) -> None:
        self.geolocator = Nominatim(user_agent="example app")

    def get_latlong(self, text):
        try:
            # myre = self.geolocator.geocode(text).raw
            myre = geocoder.osm(text).osm
            return myre
        except:
            return None
        
if __name__ == "__main__":
    ll = LatLong()
    x  = ll.get_latlong("مصر")
    print(x)