import json
import pickle

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from numpy import average


def train_model(splits, dfc, class_label, dsc_keys, fold=10, dfs_val2=None):

    models2 = []
    ypred2 = []
    aimp2 = []
    for k in range(fold):
        idsval = splits["classes"][class_label]["splits_val"][k]["ids_val"]
        idstrn = splits["classes"][class_label]["splits_val"][k]["ids_trn"]
        dfs_val = dfc[dfc.index.isin(idsval)]
        dfs_trn_ = dfc[dfc.index.isin(idstrn)]

        dfs_trn = []
        num_samples = 2000
        for cls_, df_ in dfs_trn_.groupby(by=class_label):
            df_rnd = df_.iloc[np.random.randint(0, len(df_), num_samples)]
            dfs_trn.append(df_rnd)
        dfs_trn = pd.concat(dfs_trn)
        eval_set = [((dfs_val[dsc_keys]), dfs_val[class_label])]
        cls = CatBoostClassifier(verbose=True, n_estimators=1000, eval_metric="F1", depth=6).fit(
            (dfs_trn[dsc_keys]), dfs_trn[class_label], eval_set=eval_set, use_best_model=True, early_stopping_rounds=40
        )
        models2.append(cls)
        if dfs_val2 is not None:
            y_pr = cls.predict(dfs_val2[dsc_keys])
            ypred2.append(y_pr)
        a = np.array(cls.feature_importances_)
        aimp2.append(a)

    aval = []
    for m in models2:
        av = m.best_score_["validation"]["F1"]
        aval.append(av)
    average_performance = average(aval)
    return models2, average_performance


def save_model(models, model_name, model_path, dsc_keys):
    filename = model_path + model_name + str(len(dsc_keys)) + ".sav"
    pickle.dump(models, open(filename, "wb"))
    np.savetxt(model_name + "keys.txt", list(dsc_keys), delimiter="\n", fmt="%s")
    return


def select_model(splits, dfc, class_label, dsc_keys):

    diff = 0
    keys = dsc_keys
    performance_prev = 0
    while diff > 0.1:
        models, performance = train_model(splits, dfc, class_label, keys)
        sets = list()

        for m in models:

            a = m.feature_importances_
            index = np.where(a >= 0.1)
            sets.append(set(index[0]))

        allfe = set.union(*sets)
        dsc_keys_union = list(np.array(list(keys))[list(allfe)])
        keys = dsc_keys_union
        diff = performance - performance_prev

    return models, keys


def load_data(mpath_config, filename_config, mpath_data, filename_data, class_label):

    mixed2 = pd.read_json(mpath_data + filename_data)
    dfc = mixed2[~mixed2[class_label].isna()].copy()
    with open(mpath_config + filename_config) as json_file:
        splits = json.load(json_file)
    dsc_keys = dfc.keys()
    return splits, dfc, dsc_keys


def train_pipeline():

    name_model = "keys_llps_withgonocc_retrained_"
    model_path = "/Users/hadarovi/ddcode/prediction/"
    class_label = "class1_id"
    filename_config = "model_config.json"
    filename_data = "data_model.pkl.json"
    path_config_file = "/Users/hadarovi/ddcode/prediction/models/"

    splits, dfc, dsc_keys = load_data(path_config_file, filename_config, path_config_file, filename_data, class_label)
    models, keys = select_model(splits, dfc, class_label, dsc_keys)
    save_model(models, name_model, model_path, keys)


if __name__ == "__main__":
    print("model")  # noqa: T201
