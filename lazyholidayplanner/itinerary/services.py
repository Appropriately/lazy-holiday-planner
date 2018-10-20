"""
Service objects for the itinerary app.
"""
from django.conf import settings
from django.templatetags.static import static
import os
import googlemaps

_client = googlemaps.Client(settings.GOOGLE_PLACES_API_KEY)


class GooglePlaceService:
    """
    Provides helper functions for working with the Google Places API.
    """

    @classmethod
    def _get_photo_path(cls, place_name):
        return os.path.join(settings.MEDIA_ROOT, 'images/places/',
                            place_name)

    @classmethod
    def _get_photo_url(cls, place_name):
        return os.path.join('/', settings.MEDIA_URL, 'images/places/',
                            place_name)

    @classmethod
    def _fetch_photo_from_web(cls, place_name):
        """
        Get an image for a particular place from Google and save it to the
        media folder.
        :param place_name: the name of the place to get a photo for
        """
        place = _client.places(query=place_name)['results'][0]
        photo_reference = place['photos'][0]['photo_reference']
        file_path = cls._get_photo_path(place_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w+b') as f:
            for chunk in _client.places_photo(photo_reference, max_width=1600):
                if chunk:
                    f.write(chunk)

    @classmethod
    def get_photo(cls, place_name):
        """
        Get a URL to a photo of a place.
        :param place_name: the place to get a photo of
        :return: a URI to an image file
        """
        file_path = cls._get_photo_path(place_name)
        if not os.path.exists(file_path):
            try:
                cls._fetch_photo_from_web(place_name)
            except (IndexError, IOError):
                return static('images/manchester.jpeg')
        return cls._get_photo_url(place_name)
