"""
Pricing calculator with business rules for TezzaWorks
Handles volume discounts, customization costs, and profit margin calculations
"""

class PricingCalculator:
    """
    Dynamic pricing calculator for corporate gift orders
    """

    # Volume discount tiers
    VOLUME_TIERS = [
        {'min': 500, 'max': float('inf'), 'discount': 0.25},  # 25% discount
        {'min': 101, 'max': 499, 'discount': 0.15},           # 15% discount
        {'min': 26, 'max': 100, 'discount': 0.10},            # 10% discount
        {'min': 1, 'max': 25, 'discount': 0.00},              # No discount
    ]

    # Default rates
    DEFAULT_LABOR_RATE = 25.00  # $ per hour
    DEFAULT_OVERHEAD_PERCENTAGE = 30.0  # %
    DEFAULT_TAX_RATE = 8.5  # %
    LOGO_CUSTOMIZATION_TIME = 0.25  # hours per item
    PERSONALIZATION_TIME = 0.25  # hours per item

    @staticmethod
    def get_volume_discount(quantity):
        """
        Get discount percentage based on quantity

        Args:
            quantity (int): Order quantity

        Returns:
            float: Discount percentage (0.0 to 1.0)
        """
        for tier in PricingCalculator.VOLUME_TIERS:
            if tier['min'] <= quantity <= tier['max']:
                return tier['discount']
        return 0.0

    @staticmethod
    def calculate_unit_price(base_cost, overhead_percentage, quantity,
                            has_customization=False, customization_cost=0.0):
        """
        Calculate price per unit with volume discounts

        Args:
            base_cost (float): Material cost per unit
            overhead_percentage (float): Overhead allocation percentage
            quantity (int): Order quantity
            has_customization (bool): Whether customization is included
            customization_cost (float): Additional cost for customization

        Returns:
            float: Price per unit
        """
        # Base price with overhead
        base_price = base_cost * (1 + overhead_percentage / 100)

        # Apply volume discount
        discount = PricingCalculator.get_volume_discount(quantity)
        discounted_price = base_price * (1 - discount)

        # Add customization cost
        if has_customization:
            discounted_price += customization_cost

        return round(discounted_price, 2)

    @staticmethod
    def calculate_suggested_retail_price(base_cost, overhead_percentage,
                                        target_margin=40.0):
        """
        Calculate suggested retail price based on target profit margin

        Args:
            base_cost (float): Material cost per unit
            overhead_percentage (float): Overhead allocation percentage
            target_margin (float): Target profit margin percentage

        Returns:
            float: Suggested retail price
        """
        total_cost = base_cost * (1 + overhead_percentage / 100)

        # Calculate price needed to achieve target margin
        # Price = Cost / (1 - Margin%)
        suggested_price = total_cost / (1 - target_margin / 100)

        return round(suggested_price, 2)

    @staticmethod
    def calculate_profit_margin(selling_price, total_cost):
        """
        Calculate profit margin percentage

        Args:
            selling_price (float): Selling price per unit
            total_cost (float): Total cost per unit

        Returns:
            float: Profit margin percentage
        """
        if selling_price > 0:
            margin = ((selling_price - total_cost) / selling_price) * 100
            return round(margin, 2)
        return 0.0

    @staticmethod
    def calculate_order_costs(items, labor_rate=None):
        """
        Calculate comprehensive costs for an order

        Args:
            items (list): List of order items with product details
            labor_rate (float): Hourly labor rate (uses default if None)

        Returns:
            dict: Dictionary containing cost breakdown
        """
        if labor_rate is None:
            labor_rate = PricingCalculator.DEFAULT_LABOR_RATE

        materials_cost = 0.0
        labor_hours = 0.0
        overhead_cost = 0.0

        for item in items:
            # Materials cost
            materials_cost += item['base_cost'] * item['quantity']

            # Labor hours (base + customization)
            base_labor = item.get('labor_hours', 0) * item['quantity']
            customization_labor = 0.0

            if item.get('has_logo', False):
                customization_labor += PricingCalculator.LOGO_CUSTOMIZATION_TIME * item['quantity']

            if item.get('has_personalization', False):
                customization_labor += PricingCalculator.PERSONALIZATION_TIME * item['quantity']

            labor_hours += base_labor + customization_labor

            # Overhead cost
            item_cost = item['base_cost'] * item['quantity']
            overhead_pct = item.get('overhead_percentage', PricingCalculator.DEFAULT_OVERHEAD_PERCENTAGE)
            overhead_cost += item_cost * (overhead_pct / 100)

        labor_cost = labor_hours * labor_rate
        total_cost = materials_cost + labor_cost + overhead_cost

        return {
            'materials_cost': round(materials_cost, 2),
            'labor_hours': round(labor_hours, 2),
            'labor_cost': round(labor_cost, 2),
            'overhead_cost': round(overhead_cost, 2),
            'total_cost': round(total_cost, 2),
        }

    @staticmethod
    def calculate_order_totals(subtotal, discount_percentage=0.0,
                              tax_rate=None, shipping_cost=0.0):
        """
        Calculate order totals including discounts, tax, and shipping

        Args:
            subtotal (float): Order subtotal before discounts
            discount_percentage (float): Discount percentage
            tax_rate (float): Tax rate percentage (uses default if None)
            shipping_cost (float): Shipping cost

        Returns:
            dict: Dictionary containing order totals
        """
        if tax_rate is None:
            tax_rate = PricingCalculator.DEFAULT_TAX_RATE

        # Calculate discount
        discount_amount = subtotal * (discount_percentage / 100)
        subtotal_after_discount = subtotal - discount_amount

        # Calculate tax
        tax_amount = subtotal_after_discount * (tax_rate / 100)

        # Calculate total
        total_amount = subtotal_after_discount + tax_amount + shipping_cost

        return {
            'subtotal': round(subtotal, 2),
            'discount_percentage': discount_percentage,
            'discount_amount': round(discount_amount, 2),
            'subtotal_after_discount': round(subtotal_after_discount, 2),
            'tax_rate': tax_rate,
            'tax_amount': round(tax_amount, 2),
            'shipping_cost': round(shipping_cost, 2),
            'total_amount': round(total_amount, 2),
        }

    @staticmethod
    def generate_quote(items, discount_percentage=0.0, tax_rate=None,
                      shipping_cost=0.0, labor_rate=None):
        """
        Generate comprehensive quote with pricing and costs

        Args:
            items (list): List of order items with product details
            discount_percentage (float): Discount percentage
            tax_rate (float): Tax rate percentage
            shipping_cost (float): Shipping cost
            labor_rate (float): Hourly labor rate

        Returns:
            dict: Complete quote with pricing and cost breakdown
        """
        # Calculate item totals
        item_details = []
        subtotal = 0.0

        for item in items:
            quantity = item['quantity']
            has_customization = item.get('has_logo', False) or item.get('has_personalization', False)
            customization_cost = item.get('customization_cost', 0.0)

            # Calculate unit price with volume discount
            unit_price = PricingCalculator.calculate_unit_price(
                base_cost=item['base_cost'],
                overhead_percentage=item.get('overhead_percentage', PricingCalculator.DEFAULT_OVERHEAD_PERCENTAGE),
                quantity=quantity,
                has_customization=has_customization,
                customization_cost=customization_cost
            )

            line_total = unit_price * quantity
            subtotal += line_total

            item_details.append({
                'product_name': item.get('name', 'Unknown Product'),
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': round(line_total, 2),
                'volume_discount': PricingCalculator.get_volume_discount(quantity) * 100,
                'has_customization': has_customization,
            })

        # Calculate costs
        costs = PricingCalculator.calculate_order_costs(items, labor_rate)

        # Calculate totals
        totals = PricingCalculator.calculate_order_totals(
            subtotal=subtotal,
            discount_percentage=discount_percentage,
            tax_rate=tax_rate,
            shipping_cost=shipping_cost
        )

        # Calculate overall profit margin
        profit_margin = PricingCalculator.calculate_profit_margin(
            selling_price=totals['total_amount'],
            total_cost=costs['total_cost']
        )

        return {
            'items': item_details,
            'costs': costs,
            'totals': totals,
            'profit_margin': profit_margin,
        }


# Example usage and testing
if __name__ == '__main__':
    # Example: Calculate price for 50 custom mugs
    example_items = [
        {
            'name': 'Custom Coffee Mug',
            'base_cost': 5.00,
            'overhead_percentage': 30.0,
            'labor_hours': 0.1,
            'quantity': 50,
            'has_logo': True,
            'has_personalization': False,
            'customization_cost': 2.00,
        }
    ]

    quote = PricingCalculator.generate_quote(
        items=example_items,
        discount_percentage=5.0,
        shipping_cost=25.00
    )

    print("=== TezzaWorks Quote Calculator ===")
    print(f"\nOrder Summary:")
    for item in quote['items']:
        print(f"  {item['product_name']}")
        print(f"    Quantity: {item['quantity']}")
        print(f"    Unit Price: ${item['unit_price']}")
        print(f"    Volume Discount: {item['volume_discount']}%")
        print(f"    Line Total: ${item['line_total']}")

    print(f"\nCost Breakdown:")
    print(f"  Materials: ${quote['costs']['materials_cost']}")
    print(f"  Labor ({quote['costs']['labor_hours']} hours): ${quote['costs']['labor_cost']}")
    print(f"  Overhead: ${quote['costs']['overhead_cost']}")
    print(f"  Total Cost: ${quote['costs']['total_cost']}")

    print(f"\nOrder Totals:")
    print(f"  Subtotal: ${quote['totals']['subtotal']}")
    print(f"  Discount ({quote['totals']['discount_percentage']}%): -${quote['totals']['discount_amount']}")
    print(f"  Tax ({quote['totals']['tax_rate']}%): ${quote['totals']['tax_amount']}")
    print(f"  Shipping: ${quote['totals']['shipping_cost']}")
    print(f"  TOTAL: ${quote['totals']['total_amount']}")

    print(f"\nProfit Margin: {quote['profit_margin']}%")
