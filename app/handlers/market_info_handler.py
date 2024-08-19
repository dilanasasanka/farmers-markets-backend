from models.models import FarmersMarket
from app.db_control import Session
from sqlalchemy import func

class MarketInfoHandler:
    def __init__(self, market_handler):
        self.market_handler = market_handler

    def get_market_info(self, listing_id):
        session = Session()
        try:
            market = session.query(FarmersMarket).filter_by(listing_id=listing_id).first()
            if market:
                market_details = self.formulate_content(market)
                return market_details
            else:
                return {'error': 'Market not found for the given listing_id'}
        except Exception as e:
            print(f"Error fetching market details: {e}")
            return {'error': 'An error occurred while fetching market details'}
        finally:
            session.close()

    def formulate_content(self, market):
        content_pages = self.formulate_content_pages(market)
        faq = self.formulate_faq(market)
        similar_query = self.formulate_categories(market)
        market_details = {
            'content_pages': content_pages,
            'faq': faq,
            'listing_location': market.location_address,
            'listing_id': market.listing_id,
            'listing_name': market.listing_name,
            'random_markets': self.get_random_markets(),  # Define random markets
            'similar_query': similar_query
        }
        return market_details

    def formulate_content_pages(self, market):
        summary_sentences = []

        # Construct summary dynamically based on available facts
        if market.location_address:
            summary_sentences.append(f"The market is located at {market.location_address}.")
        if market.orgnization:
            summary_sentences.append(f"It is organized by {market.orgnization}.")
        if market.diversegroup:
            summary_sentences.append(f"The market promotes diversity and includes {market.diversegroup}.")
        if market.specialproductionmethods:
            summary_sentences.append(f"Various production and practice methods are employed, including {market.specialproductionmethods}.")
        if market.acceptedpayment:
            summary_sentences.append(f"Multiple payment methods are accepted, such as {market.acceptedpayment}.")
        if market.FNAP:
            summary_sentences.append(f"The market participates in various food and nutrition assistance programs, including {market.FNAP}.")
        if market.listing_desc:
            summary_sentences.append(market.listing_desc)
        if market.location_desc:
            summary_sentences.append(market.location_desc)
        if market.location_site:
            summary_sentences.append(f"The market's location site is, {market.location_site}.")
        if market.location_indoor:
            summary_sentences.append(f"The market indoor location is {market.location_indoor}.")
        if market.saleschannel_onlineorder:
            summary_sentences.append(f"Online ordering is available at {market.saleschannel_onlineorder}")

        # Combine the sentences into a single summary paragraph
        summary = ' '.join(summary_sentences)

        facts = [
            {'title': 'Organizations', 'content': market.orgnization.split(';') if market.orgnization else []},
            {'title': 'Diversity', 'content': market.diversegroup.split(';') if market.diversegroup else []},
            {'title': 'Production/Practice Methods', 'content': market.specialproductionmethods.split(';') if market.specialproductionmethods else []},
            {'title': 'Accepted Payments', 'content': market.acceptedpayment.split(';') if market.acceptedpayment else []},
            {'title': 'Accepted Food and Nutrition Assistance Programs', 'content': market.FNAP.split(';') if market.FNAP else []},
            {'title': 'Listing Description', 'content': market.listing_desc.split(';') if market.listing_desc else []},
            {'title': 'Location Description', 'content': market.location_desc.split(';') if market.location_desc else []},
            {'title': 'Location Site', 'content': market.location_site.split(';') if market.location_site else []},
            {'title': 'Indoor Market', 'content': market.location_indoor.split(';') if market.location_indoor else []},
            {'title': 'Online Ordering', 'content': market.saleschannel_onlineorder.split(';') if market.saleschannel_onlineorder else []}
            # Add more facts as needed
        ]
        content_pages = [
            {
                'title': 'Overview',
                'summary': summary,
                'facts': facts
            }
        ]
        return content_pages

    def formulate_faq(self, market):
        faq_body = []

        # FAQ 1: What organizations is {listing_name} apart of?
        if market.orgnization:
            faq_body.append({
                'question': f"What organizations is {market.listing_name} apart of?",
                'answer': f"{market.listing_name} is apart of {market.orgnization}."
            })

        # FAQ 2: Is {location_name} affiliated with any diversity groups?
        if market.diversegroup:
            faq_body.append({
                'question': f"Is {market.listing_name} affiliated with any diversity groups?",
                'answer': f"Yes, {market.listing_name} is apart of {market.diversegroup}."
            })

        # FAQ 3: What special production methods are used at {location_name}?
        if market.specialproductionmethods:
            faq_body.append({
                'question': f"What special production methods are used at {market.listing_name}?",
                'answer': f"{market.listing_name} uses production methods like {market.specialproductionmethods} in their products."
            })

        # FAQ 4: Does {listing_name} support online orders?
        if market.saleschannel_onlineorder:
            faq_body.append({
                'question': f"Does {market.listing_name} support online orders?",
                'answer': f"Yes, {market.listing_name} supports online orders."
            })

        # FAQ 5: What payment methods does {listing_name} accept?
        if market.acceptedpayment:
            faq_body.append({
                'question': f"What payment methods does {market.listing_name} accept?",
                'answer': f"{market.listing_name} accepts {market.acceptedpayment}."
            })

        # FAQ 6: Can I use my Food Nutrition Assistance Programs (FNAP) at {listing_name}?
        if market.FNAP:
            faq_body.append({
                'question': f"Can I use my Food Nutrition Assistance Programs (FNAP) at {market.listing_name}?",
                'answer': f"Yes, {market.listing_name} accepts {market.FNAP}."
            })

        faq = {
            'faq_title': f"Frequently Asked Questions about {market.listing_name}",
            'faq_body': faq_body
        }
        return faq

    def formulate_categories(self, market):
        query_params = {
            'diversity': self.map_to_key(market.diversegroup, self.market_handler.diverse_groups),
            'production': self.map_to_key(market.specialproductionmethods, self.market_handler.production_methods),
            'payments': self.map_to_key(market.acceptedpayment, self.market_handler.accepted_payments),
            'fnap': self.map_to_key(market.FNAP, self.market_handler.fnap_methods),
        }

        # Pass the query parameters to the query_results function to get results
        market_results = self.market_handler.query_results({'filter_params': query_params})

        # Extract query_params and title from market_results
        similar_queries = {
            'query_params': query_params,
            'title': market_results.get('title', {})
        }

        return similar_queries

    def map_to_key(self, input_string, mapping):
        if input_string is None:
            return next(iter(mapping))  # Return the first key as default

        input_string_lower = input_string.lower()
        for key, value in mapping.items():
            if value.lower() in input_string_lower:
                return key
        return next(iter(mapping))  # Return the first key if no match is found

    def get_random_markets(self):
        # Implement method to fetch random markets
        session = Session()
        try:
            random_markets = session.query(FarmersMarket).order_by(func.random()).limit(3).all()
            random_market_data = [{'listing_id': market.listing_id, 'listing_name': market.listing_name} for market in random_markets]
            return random_market_data
        except Exception as e:
            # Handle exceptions
            pass
        finally:
            session.close()

