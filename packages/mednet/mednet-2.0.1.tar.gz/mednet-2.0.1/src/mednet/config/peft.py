# SPDX-FileCopyrightText: Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Functions to retrieve the correct PEFT configuration, check `PEFT configurations and models <https://huggingface.co/docs/peft/tutorial/peft_model_config>`_."""

from peft import LoraConfig


def get_lora_config(
    target_modules: list[str] | str | None,
    modules_to_save: list[str],
    rank: int = 8,
    alpha: int = 8,
    lora_dropout: float = 0.0,
    use_rslora: bool = False,
) -> LoraConfig:
    """Create and return a LoraConfig object with the specified parameters.

    This utility simplifies the instantiation of a LoraConfig for applying
    Low-Rank Adaptation (LoRA) to a model. It allows customization of target
    modules, rank, scaling factor, dropout, and optional support for Rank-Stabilized LoRA.

    Parameters
    ----------
    target_modules
        The names of the modules to apply the adapter to. If this is specified, only the modules with the specified
        names will be replaced. When passing a string, a regex match will be performed. When passing a list of
        strings, either an exact match will be performed or it is checked if the name of the module ends with any
        of the passed strings. If this is specified as 'all-linear', then all linear/Conv1D modules are chosen (if
        the model is a PreTrainedModel, the output layer excluded). If this is not specified, modules will be
        chosen according to the model architecture. If the architecture is not known, an error will be raised -- in
        this case, you should specify the target modules manually.
    modules_to_save
        List of modules apart from adapter layers to be set as trainable and saved in the final checkpoint.
    rank
        Lora approximation matrices dimension.
    alpha
        The alpha parameter for Lora scaling.
    lora_dropout
        The dropout probability for Lora layers.
    use_rslora
        When set to True, uses `Rank-Stabilized LoRA <https://doi.org/10.48550/arXiv.2312.03732>`_ which
        sets the adapter scaling factor to `lora_alpha/math.sqrt(r)`, since it was proven to work better.
        Otherwise, it will use the original default value of `lora_alpha/r`.

    Returns
    -------
        A LoraConfig object.
    """

    return LoraConfig(
        r=rank,
        lora_alpha=alpha,
        target_modules=target_modules,
        lora_dropout=lora_dropout,
        modules_to_save=modules_to_save,
        use_rslora=use_rslora,
    )
