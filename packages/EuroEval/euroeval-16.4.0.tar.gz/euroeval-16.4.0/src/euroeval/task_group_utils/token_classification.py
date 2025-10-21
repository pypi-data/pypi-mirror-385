"""Utility functions related to the token-classification task group."""

import logging
import typing as t
from copy import deepcopy

import numpy as np

from ..exceptions import InvalidBenchmark
from ..logging_utils import log
from ..utils import (
    extract_json_dict_from_string,
    raise_if_model_output_contains_nan_values,
)

if t.TYPE_CHECKING:
    from datasets.arrow_dataset import Dataset
    from transformers.tokenization_utils import PreTrainedTokenizer
    from transformers.tokenization_utils_base import BatchEncoding
    from transformers.trainer_utils import EvalPrediction

    from ..data_models import BenchmarkConfig, DatasetConfig, GenerativeModelOutput
    from ..types import Labels, Predictions


def compute_metrics(
    model_outputs_and_labels: "tuple[Predictions, Labels] | EvalPrediction",
    has_misc_tags: bool,
    dataset_config: "DatasetConfig",
    benchmark_config: "BenchmarkConfig",
    dataset: "Dataset",
) -> dict[str, float]:
    """Compute the metrics needed for evaluation.

    Args:
        model_outputs_and_labels:
            The first array contains the probability predictions and the second
            array contains the true labels.
        has_misc_tags:
            Whether the dataset has MISC tags.
        dataset_config:
            The configuration of the dataset.
        benchmark_config:
            The configuration of the benchmark.
        dataset:
            The dataset used for evaluation. This is only used in case any additional
            metadata is used to compute the metrics.

    Returns:
        A dictionary with the names of the metrics as keys and the metric values as
        values.
    """
    model_outputs, labels = model_outputs_and_labels

    # If the model outputs is a pair, then the first element corresponds to the model
    # predictions
    if isinstance(model_outputs, tuple) and len(model_outputs) == 2:
        model_outputs = model_outputs[0]

    predictions: list[list[str]]
    if not isinstance(model_outputs[0][0], str):
        raw_predictions: list[list[int]] = np.argmax(model_outputs, axis=-1).tolist()

        # Remove ignored index (special tokens)
        predictions = [
            [
                dataset_config.id2label[pred_id]
                for pred_id, lbl_id in zip(pred, label)
                if lbl_id != -100
            ]
            for pred, label in zip(raw_predictions, labels)
        ]
        labels = [
            [
                (
                    dataset_config.id2label[int(lbl_id)]
                    if isinstance(lbl_id, int) or isinstance(lbl_id, np.int_)
                    else lbl_id
                )
                for lbl_id in label
                if lbl_id != -100
            ]
            for label in labels
        ]

    else:
        predictions = model_outputs  # type: ignore[assignment]

    raise_if_model_output_contains_nan_values(model_output=predictions)

    # Replace predicted tag with either MISC or O tags if they are not part of the
    # dataset
    labels_without_misc = {
        label
        for label in dataset_config.id2label.values()
        if label not in {"b-misc", "i-misc"}
    }
    ner_tag: str
    for i, prediction_list in enumerate(predictions):
        for j, ner_tag in enumerate(prediction_list):
            if ner_tag not in labels_without_misc:
                if has_misc_tags and ner_tag[:2] == "b-":
                    predictions[i][j] = "b-misc"
                elif has_misc_tags and ner_tag[:2] == "i-":
                    predictions[i][j] = "i-misc"
                else:
                    predictions[i][j] = "o"

    # Remove MISC labels from predictions
    predictions_no_misc = deepcopy(predictions)
    for i, prediction_list in enumerate(predictions_no_misc):
        for j, ner_tag in enumerate(prediction_list):
            if ner_tag[-4:] == "misc":
                predictions_no_misc[i][j] = "o"

    # Remove MISC labels from labels
    labels_no_misc: list[list[str]] = deepcopy(labels)  # type: ignore[arg-type]
    for i, label_list in enumerate(labels_no_misc):
        for j, ner_tag in enumerate(label_list):
            if (
                isinstance(ner_tag, str)
                and len(ner_tag) >= 4
                and ner_tag[-4:] == "misc"
            ):
                labels_no_misc[i][j] = "o"

    # Compute the metrics
    # We manually set the F1 metric to be 100% if both the labels and the models
    # have no NER tags in them, since this causes an error with the `compute`
    # method otherwise
    predictions_all_zero = all(
        all(ner_tag == "o" for ner_tag in prediction_list)
        for prediction_list in predictions
    )
    labels_all_zero = all(
        all(ner_tag == "o" for ner_tag in label_list) for label_list in labels
    )
    if predictions_all_zero and labels_all_zero:
        micro_f1_score: float | None = 1.0
    else:
        metric = next(
            metric
            for metric in dataset_config.task.metrics
            if metric.name == "micro_f1"
        )
        micro_f1_score = metric(
            predictions=predictions,
            references=list(labels),
            dataset=dataset,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
        )

    # Compute the metrics without MISC tags
    # We manually set the F1 metric to be 100% if both the labels and the models
    # have no NER tags in them, since this causes an error with the `compute`
    # method otherwise
    predictions_no_misc_all_zero = all(
        all(ner_tag == "o" for ner_tag in prediction_list)
        for prediction_list in predictions_no_misc
    )
    labels_no_misc_all_zero = all(
        all(ner_tag == "o" for ner_tag in label_list) for label_list in labels_no_misc
    )
    if predictions_no_misc_all_zero and labels_no_misc_all_zero:
        micro_f1_no_misc_score: float | None = 1.0
    else:
        metric = next(
            metric
            for metric in dataset_config.task.metrics
            if metric.name == "micro_f1_no_misc"
        )
        micro_f1_no_misc_score = metric(
            predictions=predictions_no_misc,
            references=labels_no_misc,
            dataset=dataset,
            dataset_config=dataset_config,
            benchmark_config=benchmark_config,
        )

    # Raise error if the metrics are invalid
    if micro_f1_score is None or micro_f1_no_misc_score is None:
        raise InvalidBenchmark("The predictions and labels are not of the same length.")

    return dict(micro_f1_no_misc=micro_f1_no_misc_score, micro_f1=micro_f1_score)


def extract_labels_from_generation(
    input_batch: dict[str, list],
    model_output: "GenerativeModelOutput",
    dataset_config: "DatasetConfig",
) -> list[t.Any]:
    """Extract the predicted labels from the generated output.

    Args:
        input_batch:
            The input batch, where the keys are the feature names and the values
            are lists with the feature values.
        model_output:
            The raw generated output of the model.
        dataset_config:
            The configuration of the dataset.

    Returns:
        The predicted labels.
    """
    tokens = input_batch["tokens"]
    predicted_labels: list[list[str]] = [["o"] * len(token_ids) for token_ids in tokens]
    for idx, raw_prediction in enumerate(model_output.sequences):
        prediction_dict = extract_json_dict_from_string(s=raw_prediction)
        if prediction_dict is None:
            continue

        prompt_label_mapping = dataset_config.prompt_label_mapping
        for prompt_tag_name, named_entities in prediction_dict.items():
            if not isinstance(named_entities, list):
                log(
                    "The model produced an invalid format for the named entities. "
                    f"Expected a list but got {type(named_entities)}. Skipping.",
                    level=logging.DEBUG,
                )
                continue
            try:
                named_entities = [str(ne) for ne in named_entities]
            except Exception:
                log(
                    "The model produced an invalid format for the named entities. "
                    f"Expected a list of strings but got {named_entities}. Skipping.",
                    level=logging.DEBUG,
                )
                continue
            try:
                tag_name = [
                    tag[2:]
                    for tag, prompt_tag in prompt_label_mapping.items()
                    if prompt_tag == prompt_tag_name
                ][0]
            except IndexError:
                log(
                    "The model produced an invalid prompt tag name, "
                    f"{prompt_tag_name}. Skipping.",
                    level=logging.DEBUG,
                )
                continue

            named_entities = [str(named_entity) for named_entity in named_entities]
            for named_entity in named_entities:
                for ne_idx, named_entity_word in enumerate(named_entity.split()):
                    for token_idx, token in enumerate(tokens[idx]):
                        if named_entity_word in token:
                            if ne_idx == 0:
                                predicted_labels[idx][token_idx] = f"b-{tag_name}"
                            elif (
                                predicted_labels[idx][token_idx] == "o"
                                and predicted_labels[idx][token_idx - 1][2:] == tag_name
                            ):
                                predicted_labels[idx][token_idx] = f"i-{tag_name}"
    return predicted_labels


def tokenize_and_align_labels(
    examples: dict, tokeniser: "PreTrainedTokenizer", label2id: dict[str, int]
) -> "BatchEncoding":
    """Tokenise all texts and align the labels with them.

    Args:
        examples:
            The examples to be tokenised.
        tokeniser:
            A pretrained tokeniser.
        label2id:
            A dictionary that converts NER tags to IDs.

    Returns:
        A dictionary containing the tokenized data as well as labels.
    """
    # Tokenise the texts. We use the `is_split_into_words` argument here because
    # the texts in our dataset are lists of words (with a label for each word)
    tokenized_inputs = tokeniser(
        examples["tokens"], is_split_into_words=True, truncation=True, padding=True
    )

    # Extract a mapping between all the tokens and their corresponding word. If the
    # tokeniser is of a "fast" variant then this can be accessed through the
    # `word_ids` method. Otherwise, we have to extract it manually.
    all_labels: list[list[int]] = list()
    labels: list[str]
    word_ids: list[int | None]
    for i, labels in enumerate(examples["labels"]):
        # Try to get the word IDs from the tokeniser
        try:
            word_ids = tokenized_inputs.word_ids(batch_index=i)

        # If the tokeniser is not of a "fast" variant, we have to extract the word
        # IDs manually
        except ValueError:
            # Get the list of words in the document
            words: list[str] = examples["tokens"][i]

            # Get the list of token IDs in the document
            tok_ids: list[int] = tokenized_inputs.input_ids[i]

            # Decode the token IDs
            tokens = tokeniser.convert_ids_to_tokens(tok_ids)
            assert isinstance(tokens, list)

            # Remove prefixes from the tokens
            prefixes_to_remove = ["▁", "##"]
            for tok_idx, tok in enumerate(tokens):
                if tok:
                    for prefix in prefixes_to_remove:
                        if tok.startswith(prefix):
                            tokens[tok_idx] = tok[len(prefix) :]

            # Replace UNK tokens with the correct word
            tokens = handle_unk_tokens(tokeniser=tokeniser, tokens=tokens, words=words)

            # Get list of special tokens. Some tokenisers do not record these
            # properly, which is why we convert the values to their indices and
            # then back to strings
            sp_toks = [
                tokeniser.convert_ids_to_tokens(tokeniser.convert_tokens_to_ids(sp_tok))
                for sp_tok in tokeniser.special_tokens_map.values()
            ]

            # Replace special tokens with `None`
            tokens_with_none = [None if tok in sp_toks else tok for tok in tokens]

            # Get the alignment between the words and the tokens, on a character
            # level
            word_idxs = [
                word_idx for word_idx, word in enumerate(words) for _ in str(word)
            ]
            token_idxs = [
                tok_idx
                for tok_idx, tok_or_none in enumerate(tokens_with_none)
                for _ in str(tok_or_none)
                if tok_or_none is not None
            ]
            alignment = list(zip(word_idxs, token_idxs))

            # Raise error if there are not as many characters in the words as in
            # the tokens. This can be due to the use of a different prefix.
            if len(word_idxs) != len(token_idxs):
                raise InvalidBenchmark(
                    "The tokens could not be aligned with the words during manual "
                    "word-token alignment. It seems that the tokeniser is neither "
                    "of the fast variant nor of a SentencePiece/WordPiece variant."
                )

            # Get the aligned word IDs
            word_ids = list()
            for tok_idx, tok_or_none in enumerate(tokens_with_none):
                if tok_or_none is None or tok_or_none == "":
                    word_ids.append(None)
                else:
                    word_idx = [
                        word_idx
                        for word_idx, token_idx in alignment
                        if token_idx == tok_idx
                    ][0]
                    word_ids.append(word_idx)

        previous_word_idx: int | None = None
        label_ids: list[int] = list()
        for word_id in word_ids:
            # Special tokens have a word id that is None. We set the label to -100
            # so they are automatically ignored in the loss function
            if word_id is None:
                label_ids.append(-100)

            # We set the label for the first token of each word
            elif word_id != previous_word_idx:
                label = labels[word_id]
                try:
                    label_id = label2id[label.lower()]
                except KeyError as e:
                    msg = f"The label {label} was not found in the model's config."
                    raise InvalidBenchmark(msg) from e
                label_ids.append(label_id)

            # For the other tokens in a word, we set the label to -100
            else:
                label_ids.append(-100)

            previous_word_idx = word_id

        all_labels.append(label_ids)
    tokenized_inputs["labels"] = all_labels
    return tokenized_inputs


def handle_unk_tokens(
    tokeniser: "PreTrainedTokenizer", tokens: list[str], words: list[str]
) -> list[str]:
    """Replace unknown tokens in the tokens with the corresponding word.

    Args:
        tokeniser:
            The tokeniser used to tokenise the words.
        tokens:
            The list of tokens.
        words:
            The list of words.

    Returns:
        The list of tokens with unknown tokens replaced by the corresponding word.
    """
    # Locate the token indices of the unknown tokens
    token_unk_idxs = [i for i, tok in enumerate(tokens) if tok == tokeniser.unk_token]

    # Locate the word indices of the words which contain an unknown token
    word_unk_idxs = [
        i
        for i, word in enumerate(words)
        if tokeniser.unk_token
        in tokeniser.convert_ids_to_tokens(
            tokeniser.encode(word, add_special_tokens=False)
        )
    ]

    # Iterate over the token index and word index pairs
    for tok_idx, word_idx in zip(token_unk_idxs, word_unk_idxs):
        # Fetch the word
        word = words[word_idx]

        # Tokenise the word, which is now a list containing at least one UNK token
        tokens_with_unk = tokeniser.convert_ids_to_tokens(
            tokeniser.encode(word, add_special_tokens=False)
        )

        # Iterate over the tokens in the word
        for possible_unk_token in tokens_with_unk:
            # If the token is not an UNK token then we remove the first occurence
            # of the content of this token from the word. The result of the `word`
            # variable will be the content of the UNK token.
            # NOTE: This is a bit hacky and not bulletproof. For instance, if the
            # word is "1925-1950" and the tokeniser splits it into ["[UNK]", "-",
            # "19", "50"], then the result will be 2519 instead of 1925. This
            # happens almost never, however, so we can live with it.
            if possible_unk_token != tokeniser.unk_token:
                word = word.replace(possible_unk_token, "", 1)

        # Replace the token with the word
        tokens[tok_idx] = word

    return tokens
