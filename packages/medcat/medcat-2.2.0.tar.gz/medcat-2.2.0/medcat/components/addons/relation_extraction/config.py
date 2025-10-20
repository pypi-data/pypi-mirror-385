import os
import logging
from transformers import PretrainedConfig

from medcat.config.config_rel_cat import ConfigRelCAT


logger = logging.getLogger(__name__)


class RelExtrBaseConfig(PretrainedConfig):
    """ Base class for the RelCAT models
    """
    name = "base-config-relcat"

    def __init__(self, pretrained_model_name_or_path, **kwargs):
        super().__init__(**kwargs)
        self.model_type = "relcat"
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.hf_model_config: PretrainedConfig = kwargs.get(
            "model_config", PretrainedConfig())

    def to_dict(self):
        output = super().to_dict()
        output["model_type"] = self.model_type
        output["pretrained_model_name_or_path"
               ] = self.pretrained_model_name_or_path
        output["model_config"] = self.hf_model_config
        return output

    def save(self, save_path: str):
        self.hf_model_config.to_json_file(
            os.path.join(save_path, "model_config.json"))

    @classmethod
    def load(cls, pretrained_model_name_or_path: str,
             relcat_config: ConfigRelCAT, **kwargs
             ) -> "RelExtrBaseConfig":

        model_config_path = os.path.join(
            pretrained_model_name_or_path, "model_config.json")
        model_config = RelExtrBaseConfig(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            relcat_config=relcat_config, **kwargs)

        if os.path.exists(model_config_path):
            if "modern-bert" in relcat_config.general.tokenizer_name or \
               "modern-bert" in relcat_config.general.model_name:
                from medcat.components.addons.relation_extraction.modernbert.config import RelExtrModernBertConfig  # noqa
                model_config = RelExtrModernBertConfig.load(
                    model_config_path, relcat_config=relcat_config, **kwargs)
            elif "bert" in relcat_config.general.tokenizer_name or \
                    "bert" in relcat_config.general.model_name:
                from medcat.components.addons.relation_extraction.bert.config import RelExtrBertConfig  # noqa
                model_config = RelExtrBertConfig.load(
                    model_config_path, relcat_config=relcat_config, **kwargs)
            elif "llama" in relcat_config.general.tokenizer_name or \
                    "llama" in relcat_config.general.model_name:
                from medcat.components.addons.relation_extraction.llama.config import RelExtrLlamaConfig  # noqa
                model_config = RelExtrLlamaConfig.load(
                    model_config_path, relcat_config=relcat_config, **kwargs)
        else:
            if pretrained_model_name_or_path:
                pretrained_path = pretrained_model_name_or_path
                model_config.hf_model_config = (
                    PretrainedConfig.from_pretrained(
                        pretrained_model_name_or_path=pretrained_path,
                        **kwargs))
            else:
                model_name = relcat_config.general.model_name
                model_config.hf_model_config = (
                    PretrainedConfig.from_pretrained(
                        pretrained_model_name_or_path=model_name, **kwargs))
            logger.info("Loaded config from : " + model_config_path)

        return model_config
