from intuned_browser.intuned_services.api_gateways.ai_api_gateway import APIGateway


class GatewayFactory:
    """Factory class for creating pre-configured gateway instances"""

    @staticmethod
    def create_ai_gateway(model: str, api_key: str | None = None) -> APIGateway:
        """
        Create a gateway instance with configuration.

        Args:
            model: The model identifier (e.g., "gpt-4o", "claude-3-sonnet")
            api_key: Optional API key for direct mode

        Returns:
            Configured APIGateway instance
        """
        return APIGateway(model=model, api_key=api_key)
