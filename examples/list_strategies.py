"""
Example: List Available Strategies

This script shows all available strategies in the registry.
"""

from src.strategies import registry


def main():
    """List all available strategies."""
    
    print("=" * 70)
    print("Smart Trade MCP - Available Strategies")
    print("=" * 70)
    print()
    
    # Get all strategies
    strategies = registry.list_strategies()
    categories = registry.get_categories()
    
    print(f"Total Strategies: {len(strategies)}")
    print(f"Categories: {', '.join(categories)}")
    print()
    
    # Group by category
    for category in sorted(categories):
        print("=" * 70)
        print(f"[{category.upper().replace('_', ' ')}]")
        print("=" * 70)
        print()
        
        category_strategies = registry.list_strategies(category=category)
        
        for strategy in category_strategies:
            print(f"Strategy: {strategy.name}")
            print(f"   Class: {strategy.class_name}")
            print(f"   Description: {strategy.description}")
            print(f"   Required Indicators: {', '.join(strategy.required_indicators)}")
            print()
            print(f"   Default Parameters:")
            for key, value in strategy.default_params.items():
                print(f"      - {key}: {value}")
            print()
    
    # Example: Get specific strategy details
    print("=" * 70)
    print("Example: Get Strategy Details")
    print("=" * 70)
    print()
    
    metadata = registry.get_metadata("rsi")
    print(f"Strategy: {metadata.name}")
    print(f"Category: {metadata.category}")
    print(f"Description: {metadata.description}")
    print()
    
    # Example: Create strategy instance
    print("=" * 70)
    print("Example: Create Strategy Instance")
    print("=" * 70)
    print()
    
    strategy = registry.get("rsi")
    print(f"Created: {strategy}")
    print(f"Name: {strategy.name}")
    print(f"Required Indicators: {strategy.get_required_indicators()}")
    print()


if __name__ == "__main__":
    main()
