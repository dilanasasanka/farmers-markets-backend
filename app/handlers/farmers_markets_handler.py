from flask import request
from sqlalchemy import func
from models.models import FarmersMarket
from app.db_control import Session
from math import radians, sin, cos, sqrt, atan2
import random   

class FarmersMarketHandler:
    def __init__(self):
        self.diverse_groups = {
            'diversegroup_1': 'Native American-Owned Business',
            'diversegroup_2': 'Minority-Owned Business',
            'diversegroup_3': 'Women-Owned Business',
            'diversegroup_4': 'Veteran-Owned Business',
            'diversegroup_5': 'LGBTQIA+ Owned Business',
            'diversegroup_6': 'Disability-Owned Business'
        }

        self.production_methods = {
            'specialproductionmethods_1': 'Organic (USDA Certified)',
            'specialproductionmethods_2': 'Non-Certified, but Practicing Organic',
            'specialproductionmethods_3': 'Certified "Naturally Grown"',
            'specialproductionmethods_4': 'Good Agricultural Practices (GAP)-Certified',
            'specialproductionmethods_5': 'No antibiotics',
            'specialproductionmethods_6': 'Non-GMO',
            'specialproductionmethods_7': 'No hormones',
            'specialproductionmethods_8': 'No pesticides',
            'specialproductionmethods_9': 'Grass Fed',
            'specialproductionmethods_10': 'Pasture-raised/free-range animals',
            'specialproductionmethods_11': 'Humane treatment of animals',
            'specialproductionmethods_12': 'Fair labor practices, living wage, fair trade, etc.',
            'specialproductionmethods_13': 'Kosher',
            'specialproductionmethods_14': 'Halal'
        }

        self.accepted_payments = {
            'acceptedpayment_1': 'Barter',
            'acceptedpayment_2': 'Volunteer Work',
            'acceptedpayment_3': 'Cash',
            'acceptedpayment_4': 'Personal Checks',
            'acceptedpayment_5': 'Commerical Checks/Accounts',
            'acceptedpayment_6': 'Debit card/Credit card'
        }

        self.fnap_methods = {
            'FNAP_1': 'WIC',
            'FNAP_2': 'SNAP',
            'FNAP_3': 'Market Bucks',
            'FNAP_4': 'WIC Farmers Market',
            'FNAP_5': 'Senior Farmers Market Nutrition Program',
            'FNAP_888': 'Other Food and Nutrition Assistance Programs'
        }

    def get_filters(self):
        city_states = self.get_unique_city_states()

        filters = {
            'diversity': [
                {'param_key': f'diversegroup_{i}', 'param_value': group}
                for i, group in enumerate(['Native American-Owned Business', 'Minority-Owned Business', 'Women-Owned Business', 'Veteran-Owned Business', 'LGBTQIA+ Owned Business', 'Disability-Owned Business'], start=1)
            ],
            'production': [
                {'param_key': f'specialproductionmethods_{i}', 'param_value': method}
                for i, method in enumerate(['Organic (USDA Certified)', 'Non-Certified, but Practicing Organic', 'Naturally Grown', 'Good Agricultural Practices (GAP)', 'No antibiotics', 'Non-GMO', 'No hormones', 'No pesticides', 'Grass Fed', 'Pasture-raised/free-range animals', 'Humane treatment of animals', 'Fair labor practices, living wage, fair trade, etc.'], start=1)
            ],
            'payments': [
                {'param_key': f'acceptedpayment_{i}', 'param_value': payment}
                for i, payment in enumerate(['Barter', 'Volunteer Work', 'Cash', 'Personal Checks', 'Commercial Checks/Accounts', 'Debit card/Credit card', 'EBT, Venmo'], start=1)
            ],
            'fnap': [
                {'param_key': f'FNAP_{i}', 'param_value': fnap}
                for i, fnap in enumerate(['WIC', 'SNAP', 'Market Bucks', 'Senior Farmers Market Nutrition Program Market Bucks', 'Accept EBT at a central location', 'PoP'], start=1)
            ],
            'city_state': [
                {'param_key': city_state, 'param_value': city_state}
                for city_state in city_states
            ]
        }

        return {'filter_options': [{'filter_key': key, 'filter_params': params, 'filter_title': title} for key, params, title in [('diversity', filters['diversity'], 'Diversity'), ('production', filters['production'], 'Production/Practice Methods'), ('payments', filters['payments'], 'Accepted Payments'), ('fnap', filters['fnap'], 'Eligible Benefits Programs'), ('city_state', filters['city_state'], 'Cities')]]}
        
    def get_unique_city_states(self) -> list:
        session = Session()
        try:
            # Query all unique city states from the location address column
            city_states = session.query(func.lower(FarmersMarket.location_address)).distinct().all()
            return [city_state[0] for city_state in city_states]
        finally:
            session.close()
    
    def query_results(self, data):
        if 'filter_params' in data:
            filters = data['filter_params']
            markets = self.get_markets_by_filters(data['filter_params'])
            slug = self.generate_slug_from_filters(data['filter_params'])
        elif 'slug_input' in data:
            if data['slug_input']:
                filters = self.parse_slug_to_filters(data['slug_input'])
                slug = data['slug_input']
            else:
                filters = {}
                slug = "farmers-markets"
            markets = self.get_markets_by_filters(filters)
        else:
            return None  # Handle invalid input

        market_details = {
            'markets': [{'listing_name': market.listing_name,
                         'location_address': market.location_address,
                         'listing_id': market.listing_id} for market in markets],
            'query_params': {'filter_params': filters},
            'title': {'seo_slug': slug,
                      'seo_title': self.convert_slug_to_seo_title(slug, filters)}  # You can replace this with actual SEO title
        }
        return market_details

    def convert_slug_to_seo_title(self, slug, filters):
        # Define words that should remain lowercase
        exceptions = ["that", "have", "products", "accept", "are", "in"]

        # Add 'farmers' and 'markets' to exceptions only if 'diversity' is not present in the filters
        if 'diversity' in filters:
            exceptions.extend(["farmers", "markets"])

        # Replace '-' with ' ', split the slug into words
        words = slug.replace('-', ' ').split()

        # Capitalize the first letter of each word except for exceptions
        seo_title = ' '.join(word.capitalize() if word.lower() not in exceptions else word for word in words)

        return seo_title

    def get_markets_by_filters(self, filters):
        session = Session()
        try:
            query = session.query(FarmersMarket)

            if 'city_state' in filters:
                # Convert the input city_state to lowercase and remove commas, etc.
                city_state_input = filters['city_state'].replace(',', '').lower()
                
                # Query the database, converting location_address to lowercase and removing commas, etc.
                query = query.filter(func.replace(func.lower(FarmersMarket.location_address), ',', '').like(f"%{city_state_input}%"))

            if 'diversity' in filters:
                diversity_column = f"{filters['diversity']}"
                query = query.filter(getattr(FarmersMarket, diversity_column) == 1)

            if 'production' in filters:
                production_column = f"{filters['production']}"
                query = query.filter(getattr(FarmersMarket, production_column) == 1)

            if 'payments' in filters:
                payment_column = f"{filters['payments']}"
                query = query.filter(getattr(FarmersMarket, payment_column) == 1)

            if 'fnap' in filters:
                fnap_column = f"{filters['fnap']}"
                query = query.filter(getattr(FarmersMarket, fnap_column) == 1)

            markets = query.all()
            return markets
        except Exception as e:
            print(f"Error querying markets: {e}")
            return []
        finally:
            session.close()

    def generate_slug_from_filters(self, filters):
        slug_parts = []

        if not filters:  # If no filters, return default slug and title
            return 'farmers-markets'

        # Add diversity part
        if 'diversity' in filters:
            diversity_part = self.get_mapping_slug_part(filters['diversity'], self.diverse_groups)
            if diversity_part:
                slug_parts.extend(diversity_part)
                slug_parts.append('Farmers-Markets-That')
        else:
            slug_parts.append('Farmers-Markets-That')  

        # Add production, payments, and fnap parts
        slug_parts.extend(self.get_mapping_slug_part(filters.get('production'), self.production_methods, 'have', 'products'))
        slug_parts.extend(self.get_mapping_slug_part(filters.get('payments'), self.accepted_payments, 'accept'))
        slug_parts.extend(self.get_mapping_slug_part(filters.get('fnap'), self.fnap_methods, 'accept'))

        # Add city_state part
        if 'city_state' in filters:
            slug_parts.extend(['are-in', filters['city_state'].replace(',', '').replace(' ', '-')])

        slug = '-'.join(slug_parts).lower()
        return slug

    def get_mapping_slug_part(self, key, mapping, *additional_parts):
        if key in mapping:
            part = mapping[key].replace(' ', '-').replace(',', '')
            return [*additional_parts, part]
        return []
    
    def parse_slug_to_filters(self, slug_input):
        filters = {}

        # Define key phrases to split slug parts
        key_phrases = ['-farmers-markets', '-that', '-have-', '-products', '-accept-', '-are-in-']

        # Initialize slug parts with the full slug input
        slug_parts = [slug_input]

        # Split the slug into parts using each key phrase
        for phrase in key_phrases:
            new_slug_parts = []
            for part in slug_parts:
                if phrase in part:
                    new_parts = part.split(phrase)
                    new_slug_parts.extend(new_parts)
                else:
                    new_slug_parts.append(part)
            slug_parts = new_slug_parts

        # Define mappings for each filter type
        diversity_mapping = {
            'native-american-owned-business': 'diversegroup_1',
            'minority-owned-business': 'diversegroup_2',
            'women-owned-business': 'diversegroup_3',
            'veteran-owned-business': 'diversegroup_4',
            'lgbtqia+-owned-business': 'diversegroup_5',
            'disability-owned-business': 'diversegroup_6'
        }

        production_mapping = {
            'organic-usda-certified': 'specialproductionmethods_1',
            'non-certified-but-practicing-organic': 'specialproductionmethods_2',
            'naturally-grown': 'specialproductionmethods_3',
            'gap-certified': 'specialproductionmethods_4',
            'no-antibiotics': 'specialproductionmethods_5',
            'non-gmo': 'specialproductionmethods_6',
            'no-hormones': 'specialproductionmethods_7',
            'no-pesticides': 'specialproductionmethods_8',
            'grass-fed': 'specialproductionmethods_9',
            'pasture-raised-free-range-animals': 'specialproductionmethods_10',
            'humane-treatment-of-animals': 'specialproductionmethods_11',
            'fair-labor-practices-living-wage-fair-trade': 'specialproductionmethods_12',
            'kosher': 'specialproductionmethods_13',
            'halal': 'specialproductionmethods_14'
        }

        payment_mapping = {
            'barter': 'acceptedpayment_1',
            'volunteer-work': 'acceptedpayment_2',
            'cash': 'acceptedpayment_3',
            'personal-checks': 'acceptedpayment_4',
            'commercial-checks-accounts': 'acceptedpayment_5',
            'debit-card-credit-card': 'acceptedpayment_6',
        }

        fnap_mapping = {
            'wic': 'FNAP_1',
            'snap': 'FNAP_2',
            'market-bucks': 'FNAP_3',
            'wic-farmers-market': 'FNAP_4',
            'senior-farmers-market-nutrition-program': 'FNAP_5',
            'other-food-nutrition-assistance-programs': 'FNAP_888'
        }

        # Iterate through each part of the slug and map it to filter parameters
        for part in slug_parts:
            if part in diversity_mapping:
                filters['diversity'] = diversity_mapping[part]
            elif part in production_mapping:
                filters['production'] = production_mapping[part]
            elif part in payment_mapping:
                filters['payments'] = payment_mapping[part]
            elif part in fnap_mapping:
                filters['fnap'] = fnap_mapping[part]
            elif part.strip():  # Check if part is not empty after removing leading/trailing spaces
                # Assume it's the city-state part
                filters['city_state'] = part.replace('-', ' ')  # Replace '-' with ' '

        return filters


    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Radius of Earth in miles
        R = 3958.8  # miles
        
        # Calculate the distance
        distance = R * c  # Distance in miles
        return distance

    def find_markets_from_radius(self, data):
        # Extract parameters from the request
        location_x = request.args.get('location_x')
        location_y = request.args.get('location_y')
        radius_in_miles = request.args.get('radius')  # Radius in miles

        # Convert location_x and location_y to float
        try:
            location_x = float(location_x)
            location_y = float(location_y)
            radius_in_miles = float(radius_in_miles)
        except ValueError as e:
            # Handle conversion error
            return {'error': f"Error converting request data: {e}"}, 400

        # Convert radius from miles to kilometers
        radius_in_km = radius_in_miles * 1.60934

        # Query the database to retrieve all farmers markets
        session = Session()
        try:
            all_markets = session.query(FarmersMarket).all()
            
            # Filter markets within the specified radius
            markets_within_radius = []
            for market in all_markets:
                if market.location_x is not None and market.location_y is not None:
                    # Calculate distance between the provided location and market location
                    distance = self.calculate_distance(location_x, location_y, market.location_x, market.location_y)
                    
                    # Include the market if it falls within the radius
                    if distance <= radius_in_km:
                        markets_within_radius.append(market)

        except Exception as e:
            # Handle database query error
            session.rollback()
            return {'error': f"Error querying database: {e}"}, 500
        finally:
            session.close()

        # Format the results as JSON
        results = [{
            'listing_id': market.listing_id,
            'listing_name': market.listing_name,
            'location_address': market.location_address,
            'location_x': market.location_x,
            'location_y': market.location_y
            # Include other fields as needed
        } for market in markets_within_radius]

        return results
