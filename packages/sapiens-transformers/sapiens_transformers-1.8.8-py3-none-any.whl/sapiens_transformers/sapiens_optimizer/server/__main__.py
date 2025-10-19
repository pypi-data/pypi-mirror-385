from __future__ import annotations
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from .settings import (Settings, ServerSettings, ModelSettings, ConfigFileSettings)
from .cli import add_args_from_model, parse_model_from_args
from .app import create_app
import argparse
import uvicorn
import os
import sys
def main():
    description = "Sapiens Optimizer python server. Host your own LLMs! 🚀"
    parser = argparse.ArgumentParser(description=description)
    add_args_from_model(parser, Settings)
    parser.add_argument("--config_file", type=str, help="Path to a config file to load.")
    server_settings: ServerSettings | None = None
    model_settings: list[ModelSettings] = []
    args = parser.parse_args()
    try:
        config_file = os.environ.get("CONFIG_FILE", args.config_file)
        if config_file:
            if not os.path.exists(config_file): raise ValueError(f"Config file {config_file} not found!")
            with open(config_file, "rb") as f:
                if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                    import yaml
                    import json
                    config_file_settings = ConfigFileSettings.model_validate_json(json.dumps(yaml.safe_load(f)))
                else: config_file_settings = ConfigFileSettings.model_validate_json(f.read())
                server_settings = ServerSettings.model_validate(config_file_settings)
                model_settings = config_file_settings.models
        else: server_settings, model_settings = parse_model_from_args(ServerSettings, args), [parse_model_from_args(ModelSettings, args)]
    except Exception as e:
        print(e, file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    assert server_settings is not None
    assert model_settings is not None
    app = create_app(server_settings=server_settings, model_settings=model_settings)
    uvicorn.run(app, host=os.getenv("HOST", server_settings.host), port=int(os.getenv("PORT", server_settings.port)), ssl_keyfile=server_settings.ssl_keyfile, ssl_certfile=server_settings.ssl_certfile)
if __name__ == "__main__": main()
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
