#
# Copyright 2021-2025 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

import abc
from datetime import datetime
import json

import pandas as pd
import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import TARGET_TYPE
from datarobot.models.project_options import ProjectOptions

from ..utils import get_id_from_response
from .api_object import APIObject

int_float_string = t.Type(int) | t.Type(float) | String(allow_blank=True)

prediction_values_trafaret = t.Dict(
    {t.Key("label", optional=True): int_float_string, t.Key("value"): t.Float}
).ignore_extra("*")

per_ngram_text_explanations_trafaret = t.Or(
    t.List(
        t.Dict(
            {
                t.Key("ngrams"): t.List(
                    t.Dict({t.Key("ending_index"): Int, t.Key("starting_index"): Int})
                ),
                t.Key("is_unknown"): t.Bool,
                t.Key("qualitative_strength"): String,
                t.Key("strength"): t.Float,
            }
        )
    ),
    t.Null,
)

prediction_explanations_entry_trafaret = t.Dict(
    {
        t.Key("label", optional=True): int_float_string,
        t.Key("feature"): String,
        t.Key("feature_value"): int_float_string,
        t.Key("strength"): t.Float,
        t.Key("qualitative_strength"): String,
        t.Key("per_ngram_text_explanations", optional=True): per_ngram_text_explanations_trafaret,
    }
).ignore_extra("*")

prediction_explanations_trafaret = t.Dict(
    {
        t.Key("row_id"): Int,
        t.Key("prediction"): int_float_string,
        t.Key("adjusted_prediction", optional=True): int_float_string,
        t.Key("prediction_values"): t.List(prediction_values_trafaret),
        t.Key("adjusted_prediction_values", optional=True): t.List(prediction_values_trafaret),
        t.Key("prediction_explanations"): t.List(prediction_explanations_entry_trafaret),
    }
).ignore_extra("*")

KEEP_ATTRS = ["data.prediction_explanations.per_ngram_text_explanations"]


class PredictionExplanationsMode:
    """Prediction explanations mode for multiclass models"""

    @abc.abstractmethod
    def get_api_parameters(self, batch_route=False):
        """Get parameters passed in corresponding API call

        Parameters
        ----------
        batch_route : bool
            Batch routes describe prediction calls with all possible parameters, so to
            distinguish explanation parameters from others they have prefix in parameters.

        Returns
        -------
        dict
        """


class TopPredictionsMode(PredictionExplanationsMode):
    """Calculate prediction explanations for the number of top predicted classes in each row.

    Attributes
    ----------
    num_top_classes : int
        Number of top predicted classes [1..10] that will be explained for each dataset row.
    """

    def __init__(self, num_top_classes):
        self.num_top_classes = num_top_classes

    def get_api_parameters(self, batch_route=False):
        if batch_route:
            return {"explanationNumTopClasses": self.num_top_classes}
        return {"numTopClasses": self.num_top_classes}


class ClassListMode(PredictionExplanationsMode):
    """Calculate prediction explanations for the specified classes in each row.

    Attributes
    ----------
    class_names : list
        List of class names that will be explained for each dataset row.
    """

    def __init__(self, class_names):
        self.class_names = class_names

    def get_api_parameters(self, batch_route=False):
        if batch_route:
            return {"explanationClassNames": self.class_names}
        return {"classNames": self.class_names}


class PredictionExplanationsInitialization(APIObject):
    """
    Represents a prediction explanations initialization of a model.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model the prediction explanations initialization is for
    prediction_explanations_sample : list of dict
        a small sample of prediction explanations that could be generated for the model
    """

    _path_template = "projects/{}/models/{}/predictionExplanationsInitialization/"
    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("prediction_explanations_sample"): t.List(prediction_explanations_trafaret),
        }
    ).allow_extra("*")

    def __init__(self, project_id, model_id, prediction_explanations_sample=None):
        self.project_id = project_id
        self.model_id = model_id
        self.prediction_explanations_sample = prediction_explanations_sample

        self._path = self._path_template.format(self.project_id, self.model_id)

    def __repr__(self):
        return "{}(project_id={}, model_id={})".format(
            type(self).__name__, self.project_id, self.model_id
        )

    @classmethod
    def get(cls, project_id, model_id):
        """
        Retrieve the prediction explanations initialization for a model.

        Prediction explanations initializations are a prerequisite for computing prediction
        explanations, and include a sample what the computed prediction explanations for a
        prediction dataset would look like.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model the prediction explanations initialization is for

        Returns
        -------
        prediction_explanations_initialization : PredictionExplanationsInitialization
            The queried instance.

        Raises
        ------
        ClientError
            If the project or model does not exist or the initialization has not been computed.
        """
        path = cls._path_template.format(project_id, model_id)
        return cls.from_location(path)

    @classmethod
    def create(cls, project_id, model_id):
        """
        Create a prediction explanations initialization for the specified model.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which initialization is requested

        Returns
        -------
        job : Job
            an instance of created async job
        """
        from .job import Job  # pylint: disable=import-outside-toplevel,cyclic-import

        response = cls._client.post(cls._path_template.format(project_id, model_id))
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    def delete(self):
        """
        Delete this prediction explanations initialization.
        """
        self._client.delete(self._path)


class PredictionExplanations(APIObject):
    """
    Represents prediction explanations metadata and provides access to computation results.

    Examples
    --------
    .. code-block:: python

        prediction_explanations = dr.PredictionExplanations.get(project_id, explanations_id)
        for row in prediction_explanations.get_rows():
            print(row)  # row is an instance of PredictionExplanationsRow

    Attributes
    ----------
    id : str
        id of the record and prediction explanations computation result
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model the prediction explanations are for
    dataset_id : str
        id of the prediction dataset prediction explanations were computed for
    max_explanations : int
        maximum number of prediction explanations to supply per row of the dataset
    threshold_low : float
        the lower threshold, below which a prediction must score in order for prediction
        explanations to be computed for a row in the dataset
    threshold_high : float
        the high threshold, above which a prediction must score in order for prediction
        explanations to be computed for a row in the dataset
    num_columns : int
        the number of columns prediction explanations were computed for
    finish_time : float
        timestamp referencing when computation for these prediction explanations finished
    prediction_explanations_location : str
        where to retrieve the prediction explanations
    source: str
        For OTV/TS in-training predictions. Holds the portion of the training dataset used to generate
        predictions.
    """

    _path_template = "projects/{}/predictionExplanationsRecords/"
    _expls_path_template = "projects/{}/predictionExplanations/"
    _training_path_template = "projects/{}/predictionExplanationsOnTrainingData/"
    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("project_id"): String,
            t.Key("model_id"): String,
            t.Key("dataset_id"): String,
            t.Key("max_explanations"): Int,
            t.Key("threshold_low", optional=True): t.Float,
            t.Key("threshold_high", optional=True): t.Float,
            t.Key("class_names", optional=True): t.List(t.String),
            t.Key("num_top_classes", optional=True): t.Int(),
            t.Key("num_columns"): Int,
            t.Key("finish_time"): t.Float,
            t.Key("prediction_explanations_location"): String,
            t.Key("source", optional=True): String,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        project_id,
        model_id,
        dataset_id,
        max_explanations,
        num_columns,
        finish_time,
        prediction_explanations_location,
        threshold_low=None,
        threshold_high=None,
        class_names=None,
        num_top_classes=None,
        source=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.dataset_id = dataset_id
        self.max_explanations = max_explanations
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.id = id
        self.num_columns = num_columns
        self.finish_time = datetime.fromtimestamp(finish_time)
        self.prediction_explanations_location = prediction_explanations_location
        self.class_names = class_names
        self.num_top_classes = num_top_classes
        self.source = source

        self._path = self._path_template.format(self.project_id)

    def __repr__(self):
        return "{}(id={}, project_id={}, model_id={})".format(
            type(self).__name__, self.id, self.project_id, self.model_id
        )

    @classmethod
    def get(cls, project_id, prediction_explanations_id):
        """
        Retrieve a specific prediction explanations metadata.

        Parameters
        ----------
        project_id : str
            id of the project the explanations belong to
        prediction_explanations_id : str
            id of the prediction explanations

        Returns
        -------
        prediction_explanations : PredictionExplanations
            The queried instance.
        """
        path = f"{cls._path_template.format(project_id)}{prediction_explanations_id}/"
        return cls.from_location(path)

    @classmethod
    def create(
        cls,
        project_id,
        model_id,
        dataset_id,
        max_explanations=None,
        threshold_low=None,
        threshold_high=None,
        mode=None,
    ):
        """
        Create prediction explanations for the specified dataset.

        In order to create PredictionExplanations for a particular model and dataset, you must
        first:

          * Compute feature impact for the model via ``datarobot.Model.get_feature_impact()``
          * Compute a PredictionExplanationsInitialization for the model via
            ``datarobot.PredictionExplanationsInitialization.create(project_id, model_id)``
          * Compute predictions for the model and dataset via
            ``datarobot.Model.request_predictions(dataset_id)``

        ``threshold_high`` and ``threshold_low`` are optional filters applied to speed up
        computation.  When at least one is specified, only the selected outlier rows will have
        prediction explanations computed. Rows are considered to be outliers if their predicted
        value (in case of regression projects) or probability of being the positive
        class (in case of classification projects) is less than ``threshold_low`` or greater than
        ``thresholdHigh``.  If neither is specified, prediction explanations will be computed for
        all rows.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        model_id : str
            id of the model for which prediction explanations are requested
        dataset_id : str
            id of the prediction dataset for which prediction explanations are requested
        threshold_low : Optional[float]
            the lower threshold, below which a prediction must score in order for prediction
            explanations to be computed for a row in the dataset. If neither ``threshold_high`` nor
            ``threshold_low`` is specified, prediction explanations will be computed for all rows.
        threshold_high : Optional[float]
            the high threshold, above which a prediction must score in order for prediction
            explanations to be computed. If neither ``threshold_high`` nor ``threshold_low`` is
            specified, prediction explanations will be computed for all rows.
        max_explanations : Optional[int]
            the maximum number of prediction explanations to supply per row of the dataset,
            default: 3.
        mode : PredictionExplanationsMode, optional
            mode of calculation for multiclass models, if not specified - server default is
            to explain only the predicted class, identical to passing TopPredictionsMode(1).


        Returns
        -------
        job: Job
            an instance of created async job
        """
        from .job import Job  # pylint: disable=import-outside-toplevel,cyclic-import

        payload = {
            "model_id": model_id,
            "dataset_id": dataset_id,
        }
        if max_explanations is not None:
            payload["max_explanations"] = max_explanations
        if threshold_low is not None:
            payload["threshold_low"] = threshold_low
        if threshold_high is not None:
            payload["threshold_high"] = threshold_high
        if mode is not None:
            payload.update(mode.get_api_parameters(batch_route=False))

        response = cls._client.post(cls._expls_path_template.format(project_id), data=payload)
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    @classmethod
    def create_on_training_data(
        cls,
        project_id,
        model_id,
        dataset_id,
        max_explanations=None,
        threshold_low=None,
        threshold_high=None,
        mode=None,
        datetime_prediction_partition=None,
    ):
        """
        Create prediction explanations for the the dataset used to train the model.
        This can be retrieved by calling ``dr.Model.get().featurelist_id``.
        For OTV and timeseries projects, ``datetime_prediction_partition`` is required and limited to the
        first backtest ('0') or holdout ('holdout').

        In order to create PredictionExplanations for a particular model and dataset, you must
        first:

          * Compute Feature Impact for the model via ``datarobot.Model.get_feature_impact()``/
          * Compute a PredictionExplanationsInitialization for the model via
            ``datarobot.PredictionExplanationsInitialization.create(project_id, model_id)``.
          * Compute predictions for the model and dataset via
            ``datarobot.Model.request_predictions(dataset_id)``.

        ``threshold_high`` and ``threshold_low`` are optional filters applied to speed up
        computation.  When at least one is specified, only the selected outlier rows will have
        prediction explanations computed. Rows are considered to be outliers if their predicted
        value (in case of regression projects) or probability of being the positive
        class (in case of classification projects) is less than ``threshold_low`` or greater than
        ``thresholdHigh``.  If neither is specified, prediction explanations will be computed for
        all rows.

        Parameters
        ----------
        project_id : str
            The ID of the project the model belongs to.
        model_id : str
            The ID of the model for which prediction explanations are requested.
        dataset_id : str
            The ID of the prediction dataset for which prediction explanations are requested.
        threshold_low : Optional[float]
            The lower threshold, below which a prediction must score in order for prediction
            explanations to be computed for a row in the dataset. If neither ``threshold_high`` nor
            ``threshold_low`` is specified, prediction explanations will be computed for all rows.
        threshold_high : Optional[float]
            The high threshold, above which a prediction must score in order for prediction
            explanations to be computed. If neither ``threshold_high`` nor ``threshold_low`` is
            specified, prediction explanations will be computed for all rows.
        max_explanations : Optional[int]
            The maximum number of prediction explanations to supply per row of the dataset
            (default: 3).
        mode : PredictionExplanationsMode, optional
            The mode of calculation for multiclass models. If not specified, the server default is
            to explain only the predicted class, identical to passing TopPredictionsMode(1).
        datetime_prediction_partition: str
            Options: '0', 'holdout' or None.
            Used only by time series and OTV projects to indicate what part of the dataset
            will be used to generate predictions for computing prediction explanation. Current
            options are '0' (first backtest) and 'holdout'.
            Note that only the validation partition of the first backtest will be used to
            generation predictions.

        Returns
        -------
        job: Job
            An instance of created async job.
        """
        from .job import Job  # pylint: disable=import-outside-toplevel,cyclic-import

        payload = {
            "model_id": model_id,
            "dataset_id": dataset_id,
        }
        if max_explanations is not None:
            payload["max_explanations"] = max_explanations
        if threshold_low is not None:
            payload["threshold_low"] = threshold_low
        if threshold_high is not None:
            payload["threshold_high"] = threshold_high
        if mode is not None:
            payload.update(mode.get_api_parameters(batch_route=False))
        if datetime_prediction_partition is not None:
            payload["datetime_prediction_partition"] = datetime_prediction_partition

        response = cls._client.post(cls._training_path_template.format(project_id), data=payload)
        job_id = get_id_from_response(response)
        return Job.get(project_id, job_id)

    @classmethod
    def list(cls, project_id, model_id=None, limit=None, offset=None):
        """
        List of prediction explanations metadata for a specified project.

        Parameters
        ----------
        project_id : str
            id of the project to list prediction explanations for
        model_id : Optional[str]
            if specified, only prediction explanations computed for this model will be returned
        limit : int or None
            at most this many results are returned, default: no limit
        offset : int or None
            this many results will be skipped, default: 0

        Returns
        -------
        prediction_explanations : list[PredictionExplanations]
        """
        response = cls._client.get(
            cls._path_template.format(project_id),
            params={"model_id": model_id, "limit": limit, "offset": offset},
        )
        r_data = response.json()
        return [cls.from_server_data(item) for item in r_data["data"]]

    def get_rows(self, batch_size=None, exclude_adjusted_predictions=True):
        """
        Retrieve prediction explanations rows.

        Parameters
        ----------
        batch_size : int or None, optional
            maximum number of prediction explanations rows to retrieve per request
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Yields
        ------
        prediction_explanations_row : PredictionExplanationsRow
            Represents prediction explanations computed for a prediction row.
        """
        page = self.get_prediction_explanations_page(
            limit=batch_size, exclude_adjusted_predictions=exclude_adjusted_predictions
        )
        while True:
            for row in page.data:
                yield PredictionExplanationsRow(**row)
            if not page.next_page:
                break
            page = PredictionExplanationsPage.from_location(page.next_page)

    def is_multiclass(self):
        """Whether these explanations are for a multiclass project or a non-multiclass project"""
        # This method will exist now only to maintain backwards compatibility.

        return (self.num_top_classes or self.class_names) and ProjectOptions.get(
            project_id=self.project_id
        ).target == TARGET_TYPE.MULTICLASS

    def is_unsupervised_clustering_or_multiclass(self):
        """Clustering and multiclass XEMP always has either one of num_top_classes or class_names
        parameters set"""
        return bool(self.num_top_classes or self.class_names)

    def get_number_of_explained_classes(self):
        """How many classes we attempt to explain for each row"""
        if self.is_unsupervised_clustering_or_multiclass():
            return self.num_top_classes or len(self.class_names)
        return 1

    def get_all_as_dataframe(self, exclude_adjusted_predictions=True):
        """
        Retrieve all prediction explanations rows and return them as a pandas.DataFrame.

        Returned dataframe has the following structure:

            - row_id : row id from prediction dataset
            - prediction : the output of the model for this row
            - adjusted_prediction : adjusted prediction values (only appears for projects that
              utilize prediction adjustments, e.g. projects with an exposure column)
            - class_0_label : a class level from the target (only appears for classification
              projects)
            - class_0_probability : the probability that the target is this class (only appears for
              classification projects)
            - class_1_label : a class level from the target (only appears for classification
              projects)
            - class_1_probability : the probability that the target is this class (only appears for
              classification projects)
            - explanation_0_feature : the name of the feature contributing to the prediction for
              this explanation
            - explanation_0_feature_value : the value the feature took on
            - explanation_0_label : the output being driven by this explanation.  For regression
              projects, this is the name of the target feature.  For classification projects, this
              is the class label whose probability increasing would correspond to a positive
              strength.
            - explanation_0_qualitative_strength : a human-readable description of how strongly the
              feature affected the prediction (e.g. '+++', '--', '+') for this explanation
            - explanation_0_per_ngram_text_explanations : Text prediction explanations data in json
              formatted string.
            - explanation_0_strength : the amount this feature's value affected the prediction
            - ...
            - explanation_N_feature : the name of the feature contributing to the prediction for
              this explanation
            - explanation_N_feature_value : the value the feature took on
            - explanation_N_label : the output being driven by this explanation.  For regression
              projects, this is the name of the target feature.  For classification projects, this
              is the class label whose probability increasing would correspond to a positive
              strength.
            - explanation_N_qualitative_strength : a human-readable description of how strongly the
              feature affected the prediction (e.g. '+++', '--', '+') for this explanation
            - explanation_N_per_ngram_text_explanations : Text prediction explanations data in json
              formatted string.
            - explanation_N_strength : the amount this feature's value affected the prediction

        For classification projects, the server does not guarantee any ordering on the prediction
        values, however within this function we sort the values so that `class_X` corresponds to
        the same class from row to row.

        Parameters
        ----------
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set this to False to include adjusted prediction values in
            the returned dataframe.

        Returns
        -------
        dataframe: pandas.DataFrame
        """
        columns = ["row_id", "prediction"]
        rows = self.get_rows(
            batch_size=1, exclude_adjusted_predictions=exclude_adjusted_predictions
        )
        first_row = next(rows)
        has_text_explanations = (
            first_row.prediction_explanations
            and "per_ngram_text_explanations" in first_row.prediction_explanations[0]
        )
        adjusted_predictions_in_data = first_row.adjusted_prediction is not None
        if adjusted_predictions_in_data:
            columns.append("adjusted_prediction")
        # for regression, length is 1; for classification, length is number of levels in target
        # i.e. 2 for binary classification
        is_classification = len(first_row.prediction_values) > 1
        # include class label/probability for classification project
        if is_classification:
            for i in range(len(first_row.prediction_values)):
                columns.extend([f"class_{i}_label", f"class_{i}_probability"])
        if self.is_unsupervised_clustering_or_multiclass():
            for class_num in range(self.get_number_of_explained_classes()):
                prefix = f"explained_class_{class_num}"
                for i in range(self.max_explanations):
                    columns.extend(
                        [
                            f"{prefix}_explanation_{i}_feature",
                            f"{prefix}_explanation_{i}_feature_value",
                            f"{prefix}_explanation_{i}_label",
                            f"{prefix}_explanation_{i}_qualitative_strength",
                            f"{prefix}_explanation_{i}_strength",
                        ]
                    )
                    if has_text_explanations:
                        columns.append(f"{prefix}_explanation_{i}_per_ngram_text_explanations")

        else:
            for i in range(self.max_explanations):
                columns.extend(
                    [
                        f"explanation_{i}_feature",
                        f"explanation_{i}_feature_value",
                        f"explanation_{i}_label",
                        f"explanation_{i}_qualitative_strength",
                        f"explanation_{i}_strength",
                    ]
                )
                if has_text_explanations:
                    columns.append(f"explanation_{i}_per_ngram_text_explanations")
        pred_expl_list = []

        for i, row in enumerate(
            self.get_rows(exclude_adjusted_predictions=exclude_adjusted_predictions)
        ):
            data = [row.row_id, row.prediction]
            if adjusted_predictions_in_data:
                data.append(row.adjusted_prediction)
            if is_classification:
                for pred_value in sorted(row.prediction_values, key=lambda x: x["label"]):
                    data.extend([pred_value["label"], pred_value["value"]])
            if self.is_unsupervised_clustering_or_multiclass():
                # Each explained class can have less then self.max_explanations and needs to be
                # padded with None separately
                current_label = ""
                explanations_per_label = self.max_explanations
                for pred_expl in row.prediction_explanations:
                    if pred_expl["label"] == current_label:
                        explanations_per_label += 1
                    else:
                        # We switched to explaining next label, check if padding is needed
                        if explanations_per_label < self.max_explanations:
                            data += [None] * (self.max_explanations - explanations_per_label) * 5
                        current_label = pred_expl["label"]
                        explanations_per_label = 1
                    data.extend(
                        [
                            pred_expl["feature"],
                            pred_expl["feature_value"],
                            pred_expl["label"],
                            pred_expl["qualitative_strength"],
                            pred_expl["strength"],
                        ]
                    )
                    if has_text_explanations:
                        data.append(
                            json.dumps(
                                pred_expl.get("per_ngram_text_explanations"), ensure_ascii=False
                            )
                        )
                pred_expl_list.append(data + [None] * (len(columns) - len(data)))
            else:
                for pred_expl in row.prediction_explanations:
                    data.extend(
                        [
                            pred_expl["feature"],
                            pred_expl["feature_value"],
                            pred_expl["label"],
                            pred_expl["qualitative_strength"],
                            pred_expl["strength"],
                        ]
                    )
                    if has_text_explanations:
                        data.append(
                            json.dumps(
                                pred_expl.get("per_ngram_text_explanations"), ensure_ascii=False
                            )
                        )
                pred_expl_list.append(data + [None] * (len(columns) - len(data)))

        return pd.DataFrame(data=pred_expl_list, columns=columns)

    def download_to_csv(self, filename, encoding="utf-8", exclude_adjusted_predictions=True):
        """
        Save prediction explanations rows into CSV file.

        Parameters
        ----------
        filename : str or file object
            path or file object to save prediction explanations rows
        encoding : string, optional
            A string representing the encoding to use in the output file, defaults to 'utf-8'
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.
        """
        df = self.get_all_as_dataframe(exclude_adjusted_predictions=exclude_adjusted_predictions)
        df.to_csv(path_or_buf=filename, header=True, index=False, encoding=encoding)

    def get_prediction_explanations_page(
        self, limit=None, offset=None, exclude_adjusted_predictions=True
    ):
        """
        Get prediction explanations.

        If you don't want use a generator interface, you can access paginated prediction
        explanations directly.

        Parameters
        ----------
        limit : int or None
            the number of records to return, the server will use a (possibly finite) default if not
            specified
        offset : int or None
            the number of records to skip, default 0
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Returns
        -------
        prediction_explanations : PredictionExplanationsPage
        """
        kwargs = {"limit": limit, "exclude_adjusted_predictions": exclude_adjusted_predictions}
        if offset:
            kwargs["offset"] = offset
        return PredictionExplanationsPage.get(self.project_id, self.id, **kwargs)

    def delete(self):
        """
        Delete these prediction explanations.
        """
        path = f"{self._path_template.format(self.project_id)}{self.id}/"
        self._client.delete(path)


class PredictionExplanationsRow:
    """
    Represents prediction explanations computed for a prediction row.

    Notes
    -----

    ``PredictionValue`` contains:

    * ``label`` : describes what this model output corresponds to.  For regression projects,
      it is the name of the target feature.  For classification projects, it is a level from
      the target feature.
    * ``value`` : the output of the prediction.  For regression projects, it is the predicted
      value of the target.  For classification projects, it is the predicted probability the
      row belongs to the class identified by the label.


    ``PredictionExplanation`` contains:

    * ``label`` : described what output was driven by this explanation.  For regression
      projects, it is the name of the target feature.  For classification projects, it is the
      class whose probability increasing would correspond to a positive strength of this
      prediction explanation.
    * ``feature`` : the name of the feature contributing to the prediction
    * ``feature_value`` : the value the feature took on for this row
    * ``strength`` : the amount this feature's value affected the prediction
    * ``qualitative_strength`` : a human-readable description of how strongly the feature
      affected the prediction. A large positive effect is denoted '+++', medium '++', small '+',
      very small '<+'. A large negative effect is denoted '---', medium '--', small '-', very
      small '<-'.

    Attributes
    ----------
    row_id : int
        which row this ``PredictionExplanationsRow`` describes
    prediction : float
        the output of the model for this row
    adjusted_prediction : float or None
        adjusted prediction value for projects that provide this information, None otherwise
    prediction_values : list
        an array of dictionaries with a schema described as ``PredictionValue``
    adjusted_prediction_values : list
        same as prediction_values but for adjusted predictions
    prediction_explanations : list
        an array of dictionaries with a schema described as ``PredictionExplanation``
    """

    def __init__(
        self,
        row_id,
        prediction,
        prediction_values,
        prediction_explanations=None,
        adjusted_prediction=None,
        adjusted_prediction_values=None,
    ):
        self.row_id = row_id
        self.prediction = prediction
        self.prediction_values = prediction_values
        self.prediction_explanations = prediction_explanations
        self.adjusted_prediction = adjusted_prediction
        self.adjusted_prediction_values = adjusted_prediction_values

    def __repr__(self):
        return "{}(row_id={}, prediction={})".format(
            type(self).__name__, self.row_id, self.prediction
        )


class PredictionExplanationsPage(APIObject):
    """
    Represents a batch of prediction explanations received by one request.

    Attributes
    ----------
    id : str
        id of the prediction explanations computation result
    data : list[dict]
        list of raw prediction explanations; each row corresponds to a row of the prediction dataset
    count : int
        total number of rows computed
    previous_page : str
        where to retrieve previous page of prediction explanations, None if current page is the
        first
    next_page : str
        where to retrieve next page of prediction explanations, None if current page is the last
    prediction_explanations_record_location : str
        where to retrieve the prediction explanations metadata
    adjustment_method : str
        Adjustment method that was applied to predictions, or 'N/A' if no adjustments were done.
    """

    _path_template = "projects/{}/predictionExplanations/"
    _converter = t.Dict(
        {
            t.Key("id"): String,
            t.Key("count"): Int,
            t.Key("previous", optional=True): String(),
            t.Key("next", optional=True): String(),
            t.Key("data"): t.List(prediction_explanations_trafaret),
            t.Key("prediction_explanations_record_location"): t.URL,
            t.Key("adjustment_method", default="N/A"): String(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        count=None,
        previous=None,
        next=None,
        data=None,
        prediction_explanations_record_location=None,
        adjustment_method=None,
    ):
        self.id = id
        self.count = count
        self.previous_page = previous
        self.next_page = next
        self.data = data
        self.prediction_explanations_record_location = prediction_explanations_record_location
        self.adjustment_method = adjustment_method

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"

    @classmethod
    def get(
        cls,
        project_id,
        prediction_explanations_id,
        limit=None,
        offset=0,
        exclude_adjusted_predictions=True,
    ):
        """
        Retrieve prediction explanations.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        prediction_explanations_id : str
            id of the prediction explanations
        limit : int or None
            the number of records to return; the server will use a (possibly finite) default if not
            specified
        offset : int or None
            the number of records to skip, default 0
        exclude_adjusted_predictions : bool
            Optional, defaults to True. Set to False to include adjusted predictions, which will
            differ from the predictions on some projects, e.g. those with an exposure column
            specified.

        Returns
        -------
        prediction_explanations : PredictionExplanationsPage
            The queried instance.
        """
        params = {
            "offset": offset,
            "exclude_adjusted_predictions": "true" if exclude_adjusted_predictions else "false",
        }
        if limit:
            params["limit"] = limit
        path = f"{cls._path_template.format(project_id)}{prediction_explanations_id}/"
        return cls.from_location(path, keep_attrs=KEEP_ATTRS, params=params)
