import pickle
from enum import Enum
from pathlib import Path

import catboost
import numpy as np
import pandas as pd

from ..exceptions import InvalidUniProtIdProvidedError
from ..files import get_go_dir_path, get_model_dir_path
from .calculation_pipeline import calculate_pipeline_automated_one, calculate_pipeline_one


class PredictionClassLabel(Enum):
    """Defines a prediction class label."""

    PRED_LLPS_PY92 = "pred_llps_py92"  # Prediction class label for 92 features excluding the GO annotation feature
    PRED_LLPS_PY18_GO2 = "pred_llps_py18_go2"  # Prediction class label including the GO annotation feature


def load_models_and_feat_keys(model_file_name: str, feature_keys_file_name: str) -> tuple[list, np.ndarray]:
    """Loads the model and feature key files into memory."""
    mpath: Path = get_model_dir_path()
    model_file_path: Path = mpath / model_file_name
    feat_keys_file_path: Path = mpath / feature_keys_file_name
    with open(model_file_path, "rb") as f:
        models = pickle.load(f)
    dsc_keys = np.genfromtxt(feat_keys_file_path, delimiter="\n", dtype=str)
    return models, dsc_keys


def get_inference_probability_single_protein(
    data, models: list, feat_keys: np.ndarray, fold: int, predicted_class_label: PredictionClassLabel
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Get inference probability and feature importance for a single protein sequence.

    Please note, that the feature importance is only collected for the specific case, when the model has been
    trained without the GO annotation features.
    """
    yprednogo_prob, yprednogo_cls = [], []
    rr = {}
    for key in feat_keys:
        rr[key] = data[key]

    rr_pd = pd.Series(rr).to_frame().T

    all_feat_importance = None
    for n in range(fold):
        curmod = models[n]
        y_pr = curmod.predict(rr_pd, prediction_type="Probability")[:, 1].copy()
        y_pr_cls = curmod.predict(rr_pd, prediction_type="Class")
        yprednogo_prob.append(y_pr)
        yprednogo_cls.append(y_pr_cls)
        if predicted_class_label == PredictionClassLabel.PRED_LLPS_PY92:
            feat_importance: np.ndarray = curmod.get_feature_importance(
                data=catboost.Pool(rr_pd), type=catboost.EFstrType.ShapValues
            )
            if all_feat_importance is None:
                all_feat_importance = np.copy(feat_importance)
            else:
                all_feat_importance = np.concatenate((all_feat_importance, feat_importance), axis=0)

    df_yprednogo = pd.DataFrame(
        data=np.array(yprednogo_prob).T,
        columns=[f"pred_llps_py92_prob_m{ii}" for ii in range(fold)],
        index=rr_pd.index,
    )
    rr_pd[predicted_class_label.value] = np.sum(yprednogo_cls, axis=0)
    data_ret: pd.DataFrame = pd.concat([rr_pd, df_yprednogo], axis=1)

    feature_importance_df: pd.DataFrame = None
    if all_feat_importance is not None:
        # Remove the last column of the ndarray - SHAP values, which is the expected value of the model prediction
        # reference: https://catboost.ai/en/docs/concepts/shap-values
        all_feat_importance = np.delete(all_feat_importance, np.s_[-1:], axis=1)
        # Convert numpy array to a Pandas DataFrame including column headers
        feature_importance_df = pd.DataFrame(all_feat_importance, columns=feat_keys)

    return data_ret, feature_importance_df


def _calculate_inference_probability(
    model_file_name: str,
    feature_keys_file_name: str,
    is_automated: bool,
    uniprot_id: str,
    output_path: str,
    fasta_file_dir: str,
    go_flag: bool,
    fold: int,
    pred_model_probability_column_name: str,
    predicted_class_label: PredictionClassLabel = PredictionClassLabel.PRED_LLPS_PY92,
) -> [np.float64, pd.DataFrame]:
    """Calculates a score and determines the importance of the difference features for a single protein sequence.

    :param model_file_name: Name of the model file (binary file).
    :param feature_keys_file_name: Name of feature key file (TEXT file).
    :param is_automated: Boolean flag to indicate if the protein sequence and the alpha fold model files should be downloaded
    automatically.
    :param uniprot_id: Identifier of the protein sequence for which the score should be calculated.
    :param output_path: Directory path where output files should be stored.
    :param fasta_file_dir: File path of the FASTA input file (provided or automatically downloaded).
    :param go_flag: Boolean flag to indicate if the GO annotation feature should be considered.
    :param fold: Represents the number of different models.
    :param pred_model_probability_column_name: Name of the column to store the probability score.
    :param predicted_class_label: Prediction class label.

    :returns: A tuple of PICNIC score and a DataFrame of feature importance for the given list of feature keys.
    """
    models, feat_keys = load_models_and_feat_keys(
        model_file_name=model_file_name, feature_keys_file_name=feature_keys_file_name
    )
    if is_automated:
        rr = calculate_pipeline_automated_one(output_path, uniprot_id, go_flag, get_go_dir_path())
    else:
        rr = calculate_pipeline_one(output_path, uniprot_id, fasta_file_dir, go_flag, get_go_dir_path())

    dddf, feat_importance_df = get_inference_probability_single_protein(
        rr, models, feat_keys, fold, predicted_class_label
    )
    prob_columns = [f"pred_llps_py92_prob_m{ii}" for ii in range(fold)]

    dddf[pred_model_probability_column_name] = np.median(dddf[prob_columns].values, axis=1)
    return dddf[pred_model_probability_column_name].iloc[0], feat_importance_df


def inference_model_with_go_one(
    fasta_dir, path_af, uniprot_id, is_automated: bool = True, fold: int = 10
) -> [np.float64, pd.DataFrame]:
    """Calculates a PICNIC score for a single protein sequence using a model trained with the GO annotation feature."""
    if not uniprot_id:
        raise InvalidUniProtIdProvidedError(uniprot_id)
    picnic_score, feat_importance = _calculate_inference_probability(
        model_file_name="modelpipe_depth6class1_id_2_llps_withgonocc_retrained_newgo18.sav",
        feature_keys_file_name="keys_llps_withgonocc_retrained_newgo_18.txt",
        is_automated=is_automated,
        uniprot_id=uniprot_id,
        output_path=path_af,
        fasta_file_dir=fasta_dir,
        go_flag=True,
        fold=fold,
        pred_model_probability_column_name="pred_llps_py18_go_prob",
        predicted_class_label=PredictionClassLabel.PRED_LLPS_PY18_GO2,
    )
    return picnic_score, feat_importance


def inference_model_without_go_one(fasta_dir, path_af, uniprot_id, is_automated: bool = True, fold: int = 10):
    """Calculates a PICNIC score for a single protein sequence using a model trained without the GO annotation feature."""
    if not uniprot_id:
        raise InvalidUniProtIdProvidedError(uniprot_id)
    picnic_score, feat_importance = _calculate_inference_probability(
        model_file_name="modelpipe_depth7class1_id_92_llps_withoutgo_24-02.sav",
        feature_keys_file_name="keys_llps_withoutgocattrue_92.txt",
        is_automated=is_automated,
        uniprot_id=uniprot_id,
        output_path=path_af,
        fasta_file_dir=fasta_dir,
        go_flag=False,
        fold=fold,
        pred_model_probability_column_name="pred_llps_py92_prob",
    )
    return picnic_score, feat_importance


def pipeline_test_one_protein():

    path_af = "../../notebooks/test_files/O95613/"
    fasta_dir = "../../notebooks/test_files/O95613/O95613.fasta.txt"
    uniprot_id = "O95613"
    path_af = "../../notebooks/test_files/Q99720/"
    fasta_dir = "../../notebooks/test_files/Q99720/Q99720.fasta.txt"
    uniprot_id = "Q99720"
    r1 = inference_model_without_go_one(fasta_dir, path_af, uniprot_id, False)
    r2 = inference_model_with_go_one(fasta_dir, path_af, uniprot_id, False)
    print(r2)  # noqa: T201
    print(r1)  # noqa: T201


def pipeline_test_one_protein_automated():

    path_af = "../../notebooks/test_files/Q99720/"
    r1 = inference_model_without_go_one(path_af, path_af, "Q99720", True)
    print(r1)  # noqa: T201
    r2 = inference_model_with_go_one(path_af, path_af, "Q99720", True)
    print(r2)  # noqa: T201


if __name__ == "__main__":
    print("main")  # noqa: T201
