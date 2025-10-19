"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
from argparse import ArgumentParser, Namespace
from typing import Any, List, Optional
from ..pipelines import Pipeline, get_supported_tasks, pipeline
from ..utils import logging
from . import BaseTransformersCLICommand
try:
    from fastapi import Body, FastAPI, HTTPException
    from fastapi.routing import APIRoute
    from pydantic import BaseModel
    from starlette.responses import JSONResponse
    from uvicorn import run
    _serve_dependencies_installed = True
except (ImportError, AttributeError):
    BaseModel = object
    def Body(*x, **y): pass
    _serve_dependencies_installed = False
logger = logging.get_logger("sapiens_transformers-cli/serving")
def serve_command_factory(args: Namespace):
    nlp = pipeline(task=args.task, model=args.model if args.model else None, config=args.config, tokenizer=args.tokenizer, device=args.device)
    return ServeCommand(nlp, args.host, args.port, args.workers)
class ServeModelInfoResult(BaseModel): infos: dict
class ServeTokenizeResult(BaseModel):
    tokens: List[str]
    tokens_ids: Optional[List[int]]
class ServeDeTokenizeResult(BaseModel): text: str
class ServeForwardResult(BaseModel): output: Any
class ServeCommand(BaseTransformersCLICommand):
    @staticmethod
    def register_subcommand(parser: ArgumentParser):
        serve_parser = parser.add_parser("serve", help="CLI tool to run inference requests through REST and GraphQL endpoints.")
        serve_parser.add_argument("--task", type=str, choices=get_supported_tasks(), help="The task to run the pipeline on")
        serve_parser.add_argument("--host", type=str, default="localhost", help="Interface the server will listen on.")
        serve_parser.add_argument("--port", type=int, default=8888, help="Port the serving will listen to.")
        serve_parser.add_argument("--workers", type=int, default=1, help="Number of http workers")
        serve_parser.add_argument("--model", type=str, help="Model's name or path to stored model.")
        serve_parser.add_argument("--config", type=str, help="Model's config name or path to stored model.")
        serve_parser.add_argument("--tokenizer", type=str, help="Tokenizer name to use.")
        serve_parser.add_argument("--device", type=int, default=-1, help="Indicate the device to run onto, -1 indicates CPU, >= 0 indicates GPU (default: -1)")
        serve_parser.set_defaults(func=serve_command_factory)
    def __init__(self, pipeline: Pipeline, host: str, port: int, workers: int):
        self._pipeline = pipeline
        self.host = host
        self.port = port
        self.workers = workers
        if not _serve_dependencies_installed: raise RuntimeError("Using serve command requires FastAPI and uvicorn. "+'Please install transformers with [serving]: pip install "sapiens_transformers[serving]". '+"Or install FastAPI and uvicorn separately.")
        else:
            logger.info(f"Serving model over {host}:{port}")
            self._app = FastAPI(routes=[APIRoute("/", self.model_info, response_model=ServeModelInfoResult, response_class=JSONResponse, methods=["GET"]), APIRoute("/tokenize", self.tokenize, response_model=ServeTokenizeResult, response_class=JSONResponse,
            methods=["POST"]), APIRoute("/detokenize", self.detokenize, response_model=ServeDeTokenizeResult, response_class=JSONResponse, methods=["POST"]), APIRoute("/forward", self.forward, response_model=ServeForwardResult, response_class=JSONResponse, methods=["POST"])], timeout=600)
    def run(self): run(self._app, host=self.host, port=self.port, workers=self.workers)
    def model_info(self): return ServeModelInfoResult(infos=vars(self._pipeline.model.config))
    def tokenize(self, text_input: str = Body(None, embed=True), return_ids: bool = Body(False, embed=True)):
        try:
            tokens_txt = self._pipeline.tokenizer.tokenize(text_input)
            if return_ids:
                tokens_ids = self._pipeline.tokenizer.convert_tokens_to_ids(tokens_txt)
                return ServeTokenizeResult(tokens=tokens_txt, tokens_ids=tokens_ids)
            else: return ServeTokenizeResult(tokens=tokens_txt)
        except Exception as e: raise HTTPException(status_code=500, detail={"model": "", "error": str(e)})
    def detokenize(self, tokens_ids: List[int] = Body(None, embed=True), skip_special_tokens: bool = Body(False, embed=True), cleanup_tokenization_spaces: bool = Body(True, embed=True)):
        try:
            decoded_str = self._pipeline.tokenizer.decode(tokens_ids, skip_special_tokens, cleanup_tokenization_spaces)
            return ServeDeTokenizeResult(model="", text=decoded_str)
        except Exception as e: raise HTTPException(status_code=500, detail={"model": "", "error": str(e)})
    async def forward(self, inputs=Body(None, embed=True)):
        if len(inputs) == 0: return ServeForwardResult(output=[], attention=[])
        try:
            output = self._pipeline(inputs)
            return ServeForwardResult(output=output)
        except Exception as e: raise HTTPException(500, {"error": str(e)})
"""
    #################################################################################################################################################################################################
    # This code library is an adaptation of the original Transformers and was designed, developed and programmed by Sapiens Technology®.                                                            #
    # Any alteration and/or disclosure of this code without prior authorization is strictly prohibited and is subject to legal action that will be forwarded by the Sapiens Technology® legal team. #
    # This set of algorithms aims to download, train, fine-tune and/or infer large language models from various sources and slopes.                                                                 #
    #################################################################################################################################################################################################
"""
