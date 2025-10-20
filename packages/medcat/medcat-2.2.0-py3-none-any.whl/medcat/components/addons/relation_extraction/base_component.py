import logging
import os

from torch.optim import AdamW
from torch.optim.lr_scheduler import MultiStepLR

from medcat.config.config_rel_cat import ConfigRelCAT
from medcat.storage.serialisers import serialise
from medcat.components.addons.relation_extraction.models import (
    RelExtrBaseModel)
from medcat.components.addons.relation_extraction.pad_seq import (
    Pad_Sequence)
from medcat.components.addons.relation_extraction.tokenizer import (
    BaseTokenizerWrapper)
from medcat.components.addons.relation_extraction.config import (
    RelExtrBaseConfig)
from medcat.components.addons.relation_extraction.ml_utils import (
    load_state, save_state)

logger = logging.getLogger(__name__)


class RelExtrBaseComponent:

    name = "base_component_rel"

    def __init__(
            self,
            tokenizer: BaseTokenizerWrapper = BaseTokenizerWrapper(),
            model: RelExtrBaseModel = None,  # type: ignore
            model_config: RelExtrBaseConfig = None,  # type: ignore
            config: ConfigRelCAT = ConfigRelCAT(),
            task: str = "train",
            init_model: bool = False):
        """ Component that holds the model and everything for RelCAT.

        Args:
            tokenizer (BaseTokenizerWrapper): The base tokenizer for RelCAT.
            model (RelExtrBaseModel): The model wrapper.
            model_config (RelExtrBaseConfig):
                The model-specific config.
            config (ConfigRelCAT): The RelCAT config.
            task (str): The task - used for checkpointing.
            init_model (bool): Loads default BERT base model, tokenizer,
                model config. Defaults to False.
        """
        self.model: RelExtrBaseModel = model
        self.tokenizer: BaseTokenizerWrapper = tokenizer
        self.relcat_config: ConfigRelCAT = config
        self.model_config: RelExtrBaseConfig = model_config
        self.optimizer: AdamW = None  # type: ignore
        self.scheduler: MultiStepLR = None  # type: ignore
        self.task: str = task
        self.epoch: int = 0
        self.best_f1: float = 0.0

        if init_model:
            model_name = self.relcat_config.general.model_name
            self.model_config = RelExtrBaseConfig.load(
                pretrained_model_name_or_path=model_name,
                relcat_config=self.relcat_config)

            self.tokenizer = BaseTokenizerWrapper.load(
                tokenizer_path=model_name,
                relcat_config=self.relcat_config)

            special_tokens = self.relcat_config.general.tokenizer_relation_annotation_special_tokens_tags  # noqa
            self.tokenizer.hf_tokenizers.add_tokens(
                special_tokens,
                special_tokens=True)

            # used in llama tokenizer, may produce issues with other tokenizers
            self.tokenizer.hf_tokenizers.add_special_tokens(
                self.relcat_config.general.tokenizer_other_special_tokens)
            self.relcat_config.general.annotation_schema_tag_ids = (
                self.tokenizer.hf_tokenizers.convert_tokens_to_ids(
                    special_tokens))
            pad_idx = self.tokenizer.get_pad_id()
            self.relcat_config.model.padding_idx = pad_idx
            self.model_config.pad_token_id = pad_idx
            self.model_config.hf_model_config.vocab_size = (
                self.tokenizer.get_size())

            self.model = RelExtrBaseModel.load(
                pretrained_model_name_or_path=model_name,
                model_config=self.model_config,
                relcat_config=self.relcat_config)

            self.model.hf_model.resize_token_embeddings(
                self.tokenizer.get_size())

        self.pad_id = self.relcat_config.model.padding_idx
        self.padding_seq = Pad_Sequence(seq_pad_value=self.pad_id,
                                        label_pad_value=self.pad_id)

        logging.basicConfig(level=self.relcat_config.general.log_level)
        logger.setLevel(self.relcat_config.general.log_level)

        logger.info("RelExtrBaseComponent initialized")

    def save(self, save_path: str) -> None:
        """ Saves model and its dependencies to specified save_path folder.
            The CDB is obviously not saved, it is however necessary to save
            the tokenizer used.

        Args:
            save_path (str): folder path in which to save the model & deps.
        """

        assert self.relcat_config is not None
        cnf_path = os.path.join(save_path, "config")
        # NOTE: this'll be saved in a folder now
        os.makedirs(cnf_path, exist_ok=True)
        serialise('json', self.relcat_config, cnf_path)

        assert self.tokenizer is not None
        self.tokenizer.save(os.path.join(save_path))

        assert self.model is not None and self.model.hf_model is not None
        self.model.hf_model.resize_token_embeddings(self.tokenizer.get_size())

        assert self.model_config is not None
        self.model_config.hf_model_config.vocab_size = (
            self.tokenizer.get_size())
        self.model_config.hf_model_config.pad_token_id = self.pad_id
        self.model_config.save(save_path)

        save_state(self.model, optimizer=self.optimizer,
                   scheduler=self.scheduler, epoch=self.epoch,
                   best_f1=self.best_f1, path=save_path,
                   model_name=self.relcat_config.general.model_name,
                   task=self.task, is_checkpoint=False, final_export=True)

    @classmethod
    def load(cls, pretrained_model_name_or_path: str = "./"
             ) -> "RelExtrBaseComponent":
        """
        Args:
            pretrained_model_name_or_path (str): Path to RelCAT model.
                Defaults to "./".

        Returns:
            RelExtrBaseComponent: component.
        """

        relcat_config = ConfigRelCAT.load(
            load_path=pretrained_model_name_or_path)
        return cls.from_relcat_config(
            relcat_config, pretrained_model_name_or_path)

    @classmethod
    def from_relcat_config(cls, relcat_config: ConfigRelCAT,
                           pretrained_model_name_or_path: str = './'
                           ) -> 'RelExtrBaseComponent':
        model_config = RelExtrBaseConfig.load(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            relcat_config=relcat_config)

        tokenizer = BaseTokenizerWrapper.load(
            tokenizer_path=pretrained_model_name_or_path,
            relcat_config=relcat_config)

        model = RelExtrBaseModel.load(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            model_config=model_config, relcat_config=relcat_config)

        model.hf_model.resize_token_embeddings(len(tokenizer.hf_tokenizers))

        optimizer = None
        scheduler = None

        epoch, best_f1 = load_state(
            model, optimizer, scheduler, path=pretrained_model_name_or_path,
            model_name=relcat_config.general.model_name,
            file_prefix=relcat_config.general.task,
            relcat_config=relcat_config)

        component = cls(model=model, tokenizer=tokenizer,
                        model_config=model_config, config=relcat_config)
        cls.epoch = epoch
        cls.best_f1 = best_f1

        return component
