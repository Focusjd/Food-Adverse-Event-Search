import json
from search_event.models import Consumer, Product, FoodAdverseEvent, ProductEvent

def load_events_from_json(file_path):
    with open(file_path, 'r') as file:
        events_data = json.load(file)

    for event_data in events_data:
        consumer_data = event_data.get('consumer', {})
        consumer, _ = Consumer.objects.get_or_create(
            age=consumer_data.get('age'),
            age_unit=consumer_data.get('age_unit'),
            gender=consumer_data.get('gender')
        )

        event = FoodAdverseEvent.objects.create(
            repot_number=event_data.get('report_number'),
            date_created=event_data.get('date_created'),
            date_started=event_data.get('date_started'),
            outcome=', '.join(event_data.get('outcomes', [])),
            reactions=', '.join(event_data.get('reactions', [])),
            consumer=consumer,
        )

        for product_data in event_data.get('products', []):
            product, _ = Product.objects.get_or_create(
                role=product_data.get('role'),
                name_brand=product_data.get('name_brand'),
                inductry_code=product_data.get('industry_code'),
                inductry_name=product_data.get('industry_name')
            )
            ProductEvent.objects.create(product=product, adverse_event=event)

