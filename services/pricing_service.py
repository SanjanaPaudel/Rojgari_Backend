import math

from services.models import PricingConfiguration


class PricingService:
    @staticmethod
    def calculate_visit_charge(distance_km):

        config = PricingConfiguration.get_config()

        # Worker is too far away
        if distance_km > float(config.maximum_service_radius):
            return {
                "success": False,
                "message": "No technicians available within the service radius.",
                "max_radius": float(config.maximum_service_radius),
            }

        # Round normally:
        # 4.49 -> 4
        # 4.50 -> 5
        rounded_distance = math.floor(distance_km + 0.5)

        visit_charge = rounded_distance * float(config.price_per_km)

        return {
            "success": True,
            "distance_km": round(distance_km, 2),
            "rounded_distance": rounded_distance,
            "price_per_km": float(config.price_per_km),
            "visit_charge": visit_charge,
        }
