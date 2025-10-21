from engine import node
from utils.llm_client import call_llm
from pathlib import Path

def call_llm_node():
    """Call LLM with a prompt template

    Supports two ways to provide prompts:
    1. prompt_template: Direct template string
    2. prompt_file: Path to template file (relative to project root)
    """

    # Metadata declaration
    metadata = {
        "id": "call_llm",
        "namespace": "common",
        "description": "Call LLM API with prompt template and context",
        "params_schema": {
            "prompt_template": {
                "type": "str",
                "default": "",
                "description": "Direct prompt template string with {placeholders}"
            },
            "prompt_file": {
                "type": "str",
                "default": "",
                "description": "Path to prompt template file (relative to project root)"
            },
            "model": {
                "type": "str",
                "default": "gpt-4",
                "description": "LLM model to use"
            },
            "temperature": {
                "type": "float",
                "default": 0.2,
                "description": "Temperature for LLM (0.0-1.0)"
            },
            "max_tokens": {
                "type": "int",
                "default": 2000,
                "description": "Maximum tokens in response"
            }
        },
        "input_keys": ["project_root"],
        "output_keys": ["llm_response"]
    }

    def prep(ctx, params):
        # 优先从文件加载模板
        template = params.get("prompt_template", "")
        prompt_file = params.get("prompt_file", "")

        if prompt_file:
            # 从文件加载模板
            file_path = Path(prompt_file)
            if not file_path.is_absolute():
                # 相对路径，相对于项目根目录
                project_root = Path(ctx.get("project_root", "."))
                file_path = project_root / prompt_file

            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    template = f.read()
            else:
                raise FileNotFoundError(f"Prompt file not found: {file_path}")

        # 防止 KeyError：允许模板里出现缺失字段
        class D(dict):
            def __missing__(self, k): return ""
        prompt = template.format_map(D(**ctx))
        return {
            "prompt": prompt,
            "model": params.get("model", "gpt-4"),
            "temperature": params.get("temperature", 0.2),
            "max_tokens": params.get("max_tokens", 2000)
        }

    def exec(prep_result, params):
        # Call LLM - let exceptions propagate to stop the flow
        resp = call_llm(
            prompt=prep_result["prompt"],
            model=prep_result["model"],
            temperature=prep_result["temperature"],
            max_tokens=prep_result["max_tokens"]
        )
        return {"success": True, "response": resp}

    def post(ctx, prep_result, exec_result, params):
        ctx["llm_response"] = exec_result["response"]
        return "llm_complete"

    node_func = node(prep=prep, exec=exec, post=post)
    node_func["metadata"] = metadata
    return node_func
