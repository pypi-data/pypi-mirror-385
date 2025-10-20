import os
from transformers import LlamaTokenizerFast
import logging

from medcat.config.config_rel_cat import ConfigRelCAT
from medcat.components.addons.relation_extraction.tokenizer import (
    BaseTokenizerWrapper)

logger = logging.getLogger(__name__)


class TokenizerWrapperLlama(BaseTokenizerWrapper):
    ''' Wrapper around a huggingface Llama tokenizer so that it works with the
    RelCAT models.

    Args:
        hf_tokenizers (`transformers.LlamaTokenizerFast`):
            A huggingface Fast Llama.
    '''
    name = "tokenizer_wrapper_llama_rel"
    pretrained_model_name_or_path = "meta-llama/Llama-3.1-8B"

    @classmethod
    def load(cls, tokenizer_path: str, relcat_config: ConfigRelCAT, **kwargs
             ) -> "TokenizerWrapperLlama":
        tokenizer = cls()
        path = os.path.join(tokenizer_path, cls.name)

        if tokenizer_path:
            tokenizer.hf_tokenizers = LlamaTokenizerFast.from_pretrained(
                path, **kwargs)
        else:
            relcat_config.general.model_name = (
                cls.pretrained_model_name_or_path)
            tokenizer.hf_tokenizers = LlamaTokenizerFast.from_pretrained(
                pretrained_model_name_or_path=relcat_config.general.model_name)
        return tokenizer
