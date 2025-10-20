from engine import node

def {{ name }}_node():
    """{{ description }}"""

    metadata = {
        "id": "{{ name }}",
        "namespace": "{{ namespace }}",
        "description": "{{ description }}",
        "params_schema": {
            # TODO: Define your parameters
            # Example:
            # "input_file": {
            #     "type": "str",
            #     "required": True,
            #     "description": "Path to input file"
            # },
        },
        "input_keys": [],   # TODO: Keys from context (e.g., ["project_root", "files"])
        "output_keys": [],  # TODO: Keys to write (e.g., ["result", "stats"])
    }

    def prep(params, context):
        """Preparation phase: Validate inputs and setup

        Args:
            params: User-provided parameters
            context: Shared context dictionary

        Returns:
            dict: Data to merge into context
        """
        # TODO: Validate parameters
        # Example:
        # if not params.get('input_file'):
        #     raise ValueError("input_file is required")

        return {}

    def exec(params, context):
        """Execution phase: Main business logic

        Args:
            params: User-provided parameters
            context: Shared context dictionary

        Returns:
            dict: Results to merge into context
        """
        # TODO: Implement your main logic here

        # Example:
        # result = process_data(params['input_file'])
        # return {"result": result, "success": True}

        return {
            "result": "TODO: Implement logic",
        }

    def post(params, context):
        """Post phase: Cleanup and finalize

        Args:
            params: User-provided parameters
            context: Shared context dictionary

        Returns:
            dict: Final data to merge into context
        """
        # TODO: Add cleanup logic if needed
        return {}

    return node(prep, exec, post, metadata=metadata)
