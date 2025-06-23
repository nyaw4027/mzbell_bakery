from .models import DeliveryZone, DeliveryPerson, Delivery
from orders.models import Order
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)

def assign_delivery_person_to_order(order):
    latitude = order.latitude
    longitude = order.longitude

    # 1. Find delivery zone for the address
    matching_zone = None
    for zone in DeliveryZone.objects.filter(is_active=True):
        if zone.is_location_in_zone(latitude, longitude):
            matching_zone = zone
            break

    if not matching_zone:
        logger.warning(f"[Delivery] No delivery zone matched for order {order.id}")
        return None

    # 2. Get available delivery persons in this zone
    available_persons = matching_zone.delivery_persons.filter(status='available', is_active=True)

    if not available_persons.exists():
        logger.warning(f"[Delivery] No available delivery person in zone {matching_zone.name} for order {order.id}")
        return None

    # 3. Assign the first available person
    delivery_person = available_persons.first()
    delivery_person.status = 'busy'
    delivery_person.save()

    # 4. Create delivery object
    delivery = Delivery.objects.create(
        order=order,
        delivery_person=delivery_person,
        status='assigned',
        estimated_arrival=timezone.now() + timezone.timedelta(minutes=matching_zone.estimated_delivery_time)
    )

    # 5. Notify delivery person via styled HTML email
    try:
        if delivery_person.user.email:
            context = {
                'delivery_person': delivery_person,
                'order': order,
                'zone': matching_zone,
                'estimated': delivery.estimated_arrival.strftime('%A, %d %B %Y at %I:%M %p'),
            }

            subject = "📦 New Delivery Assigned - MzBell's Bakery"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = delivery_person.user.email
            text_content = f"Hi {delivery_person.user.first_name}, you’ve been assigned a new delivery (Order #{order.id})."
            html_content = render_to_string('emails/assigned_delivery.html', context)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(f"[Delivery] HTML email sent to {to_email} for order {order.id}")
    except Exception as e:
        logger.error(f"[Delivery] Failed to send HTML email: {e}")

    return delivery


def geocode_address(address):
    api_key = settings.GOOGLE_MAPS_API_KEY
    if not api_key:
        return None
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
    return None
