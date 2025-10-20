import time
from engine import Node

class {{ ClassName }}(Node):
    """{{ description }}

    This is a class-based node with built-in retry logic and state management.
    """

    metadata = {
        "id": "{{ name }}",
        "namespace": "{{ namespace }}",
        "description": "{{ description }}",
        "params_schema": {
            # TODO: Define your parameters
            # Example:
            # "api_url": {
            #     "type": "str",
            #     "required": True,
            #     "description": "API endpoint URL"
            # },
        },
        "input_keys": [],   # TODO: Keys from context
        "output_keys": [],  # TODO: Keys to write
    }

    def __init__(self, max_retries=3, timeout=30, **kwargs):
        """Initialize node with configuration

        Args:
            max_retries: Maximum retry attempts
            timeout: Operation timeout in seconds
        """
        super().__init__(**kwargs)
        self.max_retries = max_retries
        self.timeout = timeout
        self.state = {}

    def prep(self, params, context):
        """Preparation phase"""
        # TODO: Validate and setup
        self.state['started_at'] = time.time()
        return {}

    def exec(self, params, context):
        """Execution phase with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # TODO: Implement your logic
                result = self._process(params, context)
                return {"result": result, "attempts": attempt + 1}
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Attempt {attempt + 1} failed: {e}")
                print(f"Retrying... ({attempt + 2}/{self.max_retries})")
                time.sleep(2 ** attempt)  # Exponential backoff
        return {}

    def post(self, params, context):
        """Cleanup phase"""
        # TODO: Cleanup logic
        elapsed = time.time() - self.state.get('started_at', 0)
        return {"elapsed_seconds": elapsed}

    def _process(self, params, context):
        """Private method: Implement your business logic here

        Args:
            params: User parameters
            context: Shared context

        Returns:
            Processed result
        """
        # TODO: Your main logic here
        raise NotImplementedError("Implement _process() method")

def {{ name }}_node():
    """Factory function to create node instance"""
    return {{ ClassName }}()
