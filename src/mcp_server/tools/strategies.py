"""Strategy listing and management tools."""

from typing import Dict, Any, Optional
from ...core.logger import logger
from ...strategies import registry


async def list_strategies(category: Optional[str] = None) -> Dict[str, Any]:
    """
    List all available trading strategies.

    Args:
        category: Optional category filter

    Returns:
        Dictionary with strategy list
    """
    logger.info(f"Listing strategies (category={category})")

    try:
        strategies = registry.list_strategies(category=category)
        categories = registry.get_categories()

        return {
            "total": len(strategies),
            "categories": categories,
            "strategies": [
                {
                    "name": s.name,
                    "class_name": s.class_name,
                    "category": s.category,
                    "description": s.description,
                    "required_indicators": s.required_indicators,
                    "default_params": s.default_params,
                }
                for s in strategies
            ],
        }

    except Exception as e:
        logger.error(f"Error listing strategies: {e}", exc_info=True)
        raise


async def get_strategy_info(name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific strategy.

    Args:
        name: Strategy name

    Returns:
        Dictionary with strategy information
    """
    logger.info(f"Getting strategy info: {name}")

    try:
        metadata = registry.get_metadata(name)

        return {
            "name": metadata.name,
            "class_name": metadata.class_name,
            "category": metadata.category,
            "description": metadata.description,
            "required_indicators": metadata.required_indicators,
            "default_params": metadata.default_params,
        }

    except KeyError:
        return {
            "error": f"Strategy not found: {name}",
        }
    except Exception as e:
        logger.error(f"Error getting strategy info: {e}", exc_info=True)
        raise


__all__ = ["list_strategies", "get_strategy_info"]
