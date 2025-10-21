# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A collection of different metrics for classification models."""

from clu import metrics as clu_metrics
import flax
import jax
import jax.numpy as jnp
from metrax import base


def _default_threshold(num_thresholds: int) -> jax.Array:
  """Returns evenly distributed `num_thresholds` between 0.0 and 1.0.

  Args:
    num_thresholds: The number of thresholds to return.

  Returns:
    Evently distributed `num_thresholds` between 0.0 and 1.0.
  """
  if num_thresholds < 2:
    raise ValueError(
        f'num_thresholds must be at least 2, but got {num_thresholds}.'
    )
  epsilon = 1e-5
  thresholds = jnp.arange(num_thresholds, dtype=jnp.float32) / (
      num_thresholds - 1
  )
  thresholds = thresholds.at[0].set(-epsilon)
  thresholds = thresholds.at[-1].set(1.0 + epsilon)
  return thresholds


@flax.struct.dataclass
class Accuracy(base.Average):
  r"""Computes accuracy, which is the frequency with which `predictions` match `labels`.

  This metric calculates the proportion of correct predictions by comparing
  `predictions` and `labels` element-wise. It is the ratio of the sum of
  weighted correct predictions to the sum of all corresponding weights.
  If no `sample_weights` are provided, weights default to 1 for each element.

  The calculation is as follows:

  .. math::
      \text{Accuracy} = \frac{\sum (\text{weight} \times \text{correct})}{\sum
      \text{weight}}

  where `correct` is 1 if `prediction == label` for an element, and 0 otherwise.
  `weight` is the `sample_weight` for that element, or 1 if no weights are
  given.
  """

  @classmethod
  def from_model_output(
      cls,
      predictions: jax.Array,
      labels: jax.Array,
      sample_weights: jax.Array | None = None,
  ) -> 'Accuracy':
    """Updates the metric state with new `predictions` and `labels`.

    This method computes element-wise equality between `predictions` and
    `labels`. The result of this comparison (a boolean array, treated as 1 for
    True and 0 for False) is then used to update the metric's `total` and
    `count`.

    Args:
      predictions: JAX array of predicted values. Expected to have a shape
        compatible with `labels` for element-wise comparison (e.g.,
        `(batch_size,)`, `(batch_size, num_classes)`, `(batch_size,
        sequence_length, num_features)`).
      labels: JAX array of true values. Expected to have a shape compatible with
        `predictions` for element-wise comparison.
      sample_weights: Optional JAX array of weights. If provided, it must be
        broadcastable to the shape of `labels` (which should also be compatible
        with `predictions`' shape).

    Returns:
      An updated instance of `Accuracy` metric.

    Raises:
      ValueError: If JAX operations (like broadcasting or arithmetic) fail due
        to incompatible shapes or types among `predictions`, `labels`, and
        `sample_weights`. For instance, if `predictions` and `labels` shapes
        are not identical and not broadcastable to a common shape for
        comparison, or if `sample_weights` cannot be broadcast to `labels`'
        shape.
    """
    correct = predictions == labels
    count = jnp.ones_like(labels, dtype=jnp.int32)
    if sample_weights is not None:
      correct = correct * sample_weights
      count = count * sample_weights
    return cls(
        total=correct.sum(),
        count=count.sum(),
    )


@flax.struct.dataclass
class Precision(clu_metrics.Metric):
  r"""Computes precision for binary classification given `predictions` and `labels`.

  It is calculated as:

  .. math::
      Precision = \frac{TP}{TP + FP}

  where:
      - TP (True Positives): Number of correctly predicted positive cases
      - FP (False Positives): Number of incorrectly predicted positive cases

  A threshold parameter (default 0.5) is used to convert probability predictions
  to binary predictions.

  Attributes:
    true_positives: The count of true positive instances from the given data,
      label, and threshold.
    false_positives: The count of false positive instances from the given data,
      label, and threshold.
  """

  true_positives: jax.Array
  false_positives: jax.Array

  @classmethod
  def empty(cls) -> 'Precision':
    return cls(
        true_positives=jnp.array(0, jnp.float32),
        false_positives=jnp.array(0, jnp.float32),
    )

  @classmethod
  def from_model_output(
      cls,
      predictions: jax.Array,
      labels: jax.Array,
      threshold: float = 0.5,
  ) -> 'Precision':
    """Updates the metric.

    Args:
      predictions: A floating point 1D vector whose values are in the range [0,
        1]. The shape should be (batch_size,).
      labels: True value. The value is expected to be 0 or 1. The shape should
        be (batch_size,).
      threshold: The threshold to use for the binary classification.

    Returns:
      Updated Precision metric. The shape should be a single scalar.

    Raises:
      ValueError: If type of `labels` is wrong or the shapes of `predictions`
      and `labels` are incompatible.
    """
    predictions = jnp.where(predictions >= threshold, 1, 0)
    true_positives = jnp.sum((predictions == 1) & (labels == 1))
    false_positives = jnp.sum((predictions == 1) & (labels == 0))

    return cls(true_positives=true_positives, false_positives=false_positives)

  def merge(self, other: 'Precision') -> 'Precision':
    return type(self)(
        true_positives=self.true_positives + other.true_positives,
        false_positives=self.false_positives + other.false_positives,
    )

  def compute(self) -> jax.Array:
    return base.divide_no_nan(
        self.true_positives, (self.true_positives + self.false_positives)
    )


@flax.struct.dataclass
class Recall(clu_metrics.Metric):
  r"""Computes recall for binary classification given `predictions` and `labels`.

  It is calculated as:

  .. math::
      Recall = \frac{TP}{TP + FN}

  where:
      - TP (True Positives): Number of correctly predicted positive cases
      - FN (False Negatives): Number of incorrectly predicted negative cases

  A threshold parameter (default 0.5) is used to convert probability predictions
  to binary predictions.

  Attributes:
    true_positives: The count of true positive instances from the given data,
      label, and threshold.
    false_negatives: The count of false negative instances from the given data,
      label, and threshold.
  """

  true_positives: jax.Array
  false_negatives: jax.Array

  @classmethod
  def empty(cls) -> 'Recall':
    return cls(
        true_positives=jnp.array(0, jnp.float32),
        false_negatives=jnp.array(0, jnp.float32),
    )

  @classmethod
  def from_model_output(
      cls, predictions: jax.Array, labels: jax.Array, threshold: float = 0.5
  ) -> 'Recall':
    """Updates the metric.

    Args:
      predictions: A floating point 1D vector whose values are in the range [0,
        1]. The shape should be (batch_size,).
      labels: True value. The value is expected to be 0 or 1. The shape should
        be (batch_size,).
      threshold: The threshold to use for the binary classification.

    Returns:
      Updated Recall metric. The shape should be a single scalar.

    Raises:
      ValueError: If type of `labels` is wrong or the shapes of `predictions`
      and `labels` are incompatible.
    """
    predictions = jnp.where(predictions >= threshold, 1, 0)
    true_positives = jnp.sum((predictions == 1) & (labels == 1))
    false_negatives = jnp.sum((predictions == 0) & (labels == 1))

    return cls(true_positives=true_positives, false_negatives=false_negatives)

  def merge(self, other: 'Recall') -> 'Recall':
    return type(self)(
        true_positives=self.true_positives + other.true_positives,
        false_negatives=self.false_negatives + other.false_negatives,
    )

  def compute(self) -> jax.Array:
    return base.divide_no_nan(
        self.true_positives, (self.true_positives + self.false_negatives)
    )


@flax.struct.dataclass
class AUCPR(clu_metrics.Metric):
  r"""Computes area under the precision-recall curve for binary classification given `predictions` and `labels`.

  The Precision-Recall curve shows the tradeoff between precision and recall at
  different
  classification thresholds. The area under this curve (AUC-PR) provides a
  single score
  that represents the model's ability to identify positive cases across
  all possible classification thresholds, particularly in imbalanced datasets.

  For each threshold :math:`t`, precision and recall are calculated as:

  .. math::
    Precision(t) = \frac{TP(t)}{TP(t) + FP(t)}

    Recall(t) = \frac{TP(t)}{TP(t) + FN(t)}

  The AUC-PR is then computed using interpolation:

  .. math::
    AUC-PR = \sum_{i=1}^{n-1} (R_{i+1} - R_i) \cdot \frac{P_i + P_{i+1}}{2}

  where:
    - :math:`P_i` is precision at threshold i
    - :math:`R_i` is recall at threshold i
    - :math:`n` is the number of thresholds

  AUC-PR Curve metric have a number of known issues so use it with caution.
  - PR curves are highly class balance sensitive.
  - PR is a non-monotonic function and thus its "area" is not directly
    proportional to performance.
  - PR-AUC has no standard implementation and different libraries will give
    different results. Some libraries will interpolate between points, others
    will assume a step function (or trapezoidal as sklearn does). Some libraries
    will compute the convex hull of the PR curve, others will not. Because PR is
    non monotonic, its value is sensitive to the number of samples along the
    curve (more so than ROC-AUC).

  Attributes:
    true_positives: The count of true positive instances from the given data and
      label at each threshold.
    false_positives: The count of false positive instances from the given data
      and label at each threshold.
    false_negatives: The count of false negative instances from the given data
      and label at each threshold.
  """

  # shape: (threshold, 1)
  true_positives: jax.Array
  false_positives: jax.Array
  false_negatives: jax.Array
  num_thresholds: int

  @classmethod
  def empty(cls) -> 'AUCPR':
    return cls(
        true_positives=jnp.array(0, jnp.float32),
        false_positives=jnp.array(0, jnp.float32),
        false_negatives=jnp.array(0, jnp.float32),
        num_thresholds=0,
    )

  @classmethod
  def from_model_output(
      cls,
      predictions: jax.Array,
      labels: jax.Array,
      sample_weights: jax.Array | None = None,
      num_thresholds: int = 200,
  ) -> 'AUCPR':
    """Updates the metric.

    Args:
      predictions: A floating point 1D vector whose values are in the range [0,
        1]. The shape should be (batch_size,).
      labels: True value. The value is expected to be 0 or 1. The shape should
        be (batch_size,).
      sample_weights: An optional floating point 1D vector representing the
        weight of each sample. The shape should be (batch_size,).
      num_thresholds: The number of thresholds to use. Default is 200.

    Returns:
      The area under the precision-recall curve. The shape should be a single
      scalar.

    Raises:
      ValueError: If type of `labels` is wrong or the shapes of `predictions`
      and `labels` are incompatible.
    """
    pred_is_pos = jnp.greater(
        predictions,
        _default_threshold(num_thresholds=num_thresholds)[..., None],
    )
    pred_is_neg = jnp.logical_not(pred_is_pos)
    label_is_pos = jnp.equal(labels, 1)
    label_is_neg = jnp.equal(labels, 0)

    true_positives = pred_is_pos * label_is_pos
    false_positives = pred_is_pos * label_is_neg
    false_negatives = pred_is_neg * label_is_pos

    if sample_weights is not None:
      true_positives = true_positives * sample_weights
      false_positives = false_positives * sample_weights
      false_negatives = false_negatives * sample_weights

    return cls(
        true_positives=true_positives.sum(axis=-1),
        false_positives=false_positives.sum(axis=-1),
        false_negatives=false_negatives.sum(axis=-1),
        num_thresholds=num_thresholds,
    )

  def merge(self, other: 'AUCPR') -> 'AUCPR':
    return type(self)(
        true_positives=self.true_positives + other.true_positives,
        false_positives=self.false_positives + other.false_positives,
        false_negatives=self.false_negatives + other.false_negatives,
        num_thresholds=self.num_thresholds,
    )

  def interpolate_pr_auc(self) -> jax.Array:
    """Interpolation formula inspired by section 4 of Davis & Goadrich 2006.

    https://minds.wisconsin.edu/handle/1793/60482

    Note here we derive & use a closed formula not present in the paper
    as follows:

      Precision = TP / (TP + FP) = TP / P

    Modeling all of TP (true positive), FP (false positive) and their sum
    P = TP + FP (predicted positive) as varying linearly within each
    interval [A, B] between successive thresholds, we get

      Precision slope = dTP / dP
                      = (TP_B - TP_A) / (P_B - P_A)
                      = (TP - TP_A) / (P - P_A)
      Precision = (TP_A + slope * (P - P_A)) / P

    The area within the interval is (slope / total_pos_weight) times

      int_A^B{Precision.dP} = int_A^B{(TP_A + slope * (P - P_A)) * dP / P}
      int_A^B{Precision.dP} = int_A^B{slope * dP + intercept * dP / P}

    where intercept = TP_A - slope * P_A = TP_B - slope * P_B, resulting in

      int_A^B{Precision.dP} = TP_B - TP_A + intercept * log(P_B / P_A)

    Bringing back the factor (slope / total_pos_weight) we'd put aside, we
    get

      slope * [dTP + intercept *  log(P_B / P_A)] / total_pos_weight

    where dTP == TP_B - TP_A.

    Note that when P_A == 0 the above calculation simplifies into

      int_A^B{Precision.dTP} = int_A^B{slope * dTP} = slope * (TP_B - TP_A)

    which is really equivalent to imputing constant precision throughout the
    first bucket having >0 true positives.

    Returns:
      pr_auc: A float scalar jax.Array that is an approximation of the area
      under the P-R curve.
    """
    dtp = (
        self.true_positives[: self.num_thresholds - 1] - self.true_positives[1:]
    )
    p = self.true_positives + self.false_positives
    dp = p[: self.num_thresholds - 1] - p[1:]
    prec_slope = base.divide_no_nan(dtp, jnp.maximum(dp, 0))
    intercept = self.true_positives[1:] - prec_slope * p[1:]

    # recall_relative_ratio
    safe_p_ratio = jnp.where(
        jnp.multiply(p[: self.num_thresholds - 1] > 0, p[1:] > 0),
        base.divide_no_nan(
            p[: self.num_thresholds - 1],
            jnp.maximum(p[1:], 0),
        ),
        jnp.ones_like(p[1:]),
    )
    # pr_auc_increment
    pr_auc_increment = base.divide_no_nan(
        prec_slope * (dtp + intercept * jnp.log(safe_p_ratio)),
        jnp.maximum(self.true_positives[1:] + self.false_negatives[1:], 0),
    )
    return jnp.sum(pr_auc_increment)

  def compute(self) -> jax.Array:
    # Use interpolation to compute the area under the PR curve to match Keras.
    return self.interpolate_pr_auc()


@flax.struct.dataclass
class AUCROC(clu_metrics.Metric):
  r"""Computes area under the receiver operation characteristic curve for binary classification given `predictions`
  and `labels`.

  The ROC curve shows the tradeoff between the true positive rate (TPR) and
  false positive
  rate (FPR) at different classification thresholds. The area under this curve
  (AUC-ROC)
  provides a single score that represents the model's ability to discriminate
  between
  positive and negative cases across all possible classification thresholds,
  regardless of class imbalance.

  For each threshold :math:`t`, TPR and FPR are calculated as:

  .. math::
      TPR(t) = \frac{TP(t)}{TP(t) + FN(t)}

      FPR(t) = \frac{FP(t)}{FP(t) + TN(t)}

  The AUC-ROC is then computed using the trapezoidal rule:

  .. math::
      AUC-ROC = \int_{0}^{1} TPR(FPR^{-1}(x)) dx

  A score of 1 represents perfect classification, while 0.5 represents random
  guessing.

  Attributes:
    true_positives: The count of true positive instances from the given data and
      label at each threshold.
    false_positives: The count of false positive instances from the given data
      and label at each threshold.
    total_count: The count of every data point.
  """

  # shape: (threshold, 1)
  true_positives: jax.Array
  true_negatives: jax.Array
  false_positives: jax.Array
  false_negatives: jax.Array
  num_thresholds: int

  @classmethod
  def empty(cls) -> 'AUCROC':
    return cls(
        true_positives=jnp.array(0, jnp.float32),
        true_negatives=jnp.array(0, jnp.float32),
        false_positives=jnp.array(0, jnp.float32),
        false_negatives=jnp.array(0, jnp.float32),
        num_thresholds=0,
    )

  @classmethod
  def from_model_output(
      cls,
      predictions: jax.Array,
      labels: jax.Array,
      sample_weights: jax.Array | None = None,
      num_thresholds: int = 200,
  ) -> 'AUCROC':
    """Updates the metric.

    Args:
      predictions: A floating point 1D vector whose values are in the range [0,
        1]. The shape should be (batch_size,).
      labels: True value. The value is expected to be 0 or 1. The shape should
        be (batch_size,).
      sample_weights: An optional floating point 1D vector representing the
        weight of each sample. The shape should be (batch_size,).
      num_thresholds: The number of thresholds to use. Default is 200.

    Returns:
      The area under the receiver operation characteristic curve. The shape
      should be a single scalar.

    Raises:
      ValueError: If type of `labels` is wrong or the shapes of `predictions`
      and `labels` are incompatible.
    """
    pred_is_pos = jnp.greater(
        predictions,
        _default_threshold(num_thresholds=num_thresholds)[..., None],
    )
    pred_is_neg = jnp.logical_not(pred_is_pos)
    label_is_pos = jnp.equal(labels, 1)
    label_is_neg = jnp.equal(labels, 0)

    true_positives = pred_is_pos * label_is_pos
    true_negatives = pred_is_neg * label_is_neg
    false_positives = pred_is_pos * label_is_neg
    false_negatives = pred_is_neg * label_is_pos

    if sample_weights is not None:
      true_positives = true_positives * sample_weights
      true_negatives = true_negatives * sample_weights
      false_positives = false_positives * sample_weights
      false_negatives = false_negatives * sample_weights

    return cls(
        true_positives=true_positives.sum(axis=-1),
        true_negatives=true_negatives.sum(axis=-1),
        false_positives=false_positives.sum(axis=-1),
        false_negatives=false_negatives.sum(axis=-1),
        num_thresholds=num_thresholds,
    )

  def merge(self, other: 'AUCROC') -> 'AUCROC':
    return type(self)(
        true_positives=self.true_positives + other.true_positives,
        true_negatives=self.true_negatives + other.true_negatives,
        false_positives=self.false_positives + other.false_positives,
        false_negatives=self.false_negatives + other.false_negatives,
        num_thresholds=self.num_thresholds,
    )

  def compute(self) -> jax.Array:
    tp_rate = base.divide_no_nan(
        self.true_positives, self.true_positives + self.false_negatives
    )
    fp_rate = base.divide_no_nan(
        self.false_positives, self.false_positives + self.true_negatives
    )
    # Threshold goes from 0 to 1, so trapezoid is negative.
    return jnp.trapezoid(tp_rate, fp_rate) * -1

@flax.struct.dataclass
class FBetaScore(clu_metrics.Metric):
    """
    F-Beta score Metric class
    Computes the F-Beta score for the binary classification given 'predictions' and 'labels'.

    Formula for F-Beta Score:
        b2 = beta ** 2
        f_beta_score = ((1 + b2) * (precision * recall)) / (precision * b2 + recall)

    F-Beta turns into the F1 Score when beta = 1.0

    Attributes:
        true_positives: The count of true positive instances from the given data,
            label, and threshold.
        false_positives: The count of false positive instances from the given data,
            label, and threshold.
        false_negatives: The count of false negative instances from the given data,
            label, and threshold.
        beta: The beta value used in the F-Score metric
    """

    true_positives: jax.Array
    false_positives: jax.Array
    false_negatives: jax.Array
    beta: float = 1.0

    # Reset the variables for the class
    @classmethod
    def empty(cls) -> 'FBetaScore':
        return cls(
            true_positives = jnp.array(0, jnp.float32),
            false_positives = jnp.array(0, jnp.float32),
            false_negatives = jnp.array(0, jnp.float32),
            beta=1.0,
        )

    @classmethod
    def from_model_output(
            cls,
            predictions: jax.Array,
            labels: jax.Array,
            beta = beta,
            threshold = 0.5,) -> 'FBetaScore':
        """Updates the metric.
            Note: When only predictions and labels are given, the score calculated
            is the F1 score if the FBetaScore beta value has not been previously modified.

            Args:
                predictions: A floating point 1D vector whose values are in the range [0,
                  1]. The shape should be (batch_size,).
                labels: True value. The value is expected to be 0 or 1. The shape should
                  be (batch_size,).
                beta: beta value to use in the F-Score metric. A floating number.
                threshold: threshold value to use in the F-Score metric. A floating number.

            Returns:
                The updated FBetaScore object.

            Raises:
                ValueError: If type of `labels` is wrong or the shapes of `predictions`
                and `labels` are incompatible. If the beta or threshold are invalid values
                an error is raised as well.
        """

        # Ensure that beta is a floating number and a valid number
        if not isinstance(beta, float):
            raise ValueError('The "Beta" value must be a floating number.')
        if beta <= 0.0:
            raise ValueError('The "Beta" value must be larger than 0.0.')

        # Ensure that threshold is a floating number and a valid number
        if not isinstance(threshold, float):
            raise ValueError('The "Threshold" value must be a floating number.')
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError('The "Threshold" value must be between 0 and 1.')

        # Modify predictions with the given threshold value
        predictions = jnp.where(predictions >= threshold, 1, 0)

        # Assign the true_positive, false_positive, and false_negative their values
        """
        We are calculating these values manually instead of using Metrax's
        precision and recall classes. This is because the Metrax versions end up
        outputting a single numerical answer when we need an array of numbers.
        """
        true_positives = jnp.sum(predictions * labels, axis = 0)
        false_positives = jnp.sum(predictions * (1 - labels), axis = 0)
        false_negatives = jnp.sum((1- predictions) * labels, axis = 0)

        return cls(true_positives = true_positives,
                   false_positives = false_positives,
                   false_negatives = false_negatives,
                   beta = beta)

    """
    This function is currently unused as the 'from_model_output' function can handle the whole
    dataset without needing to split and merge them. I'm leaving this here for now incase we want to
    repurpose this or need to change something that requires this function's use again. This function would need
    to be reworked for it to work with the current implementation of this class.
    """
    # # Merge datasets together
    # def merge(self, other: 'FBetaScore') -> 'FBetaScore':
    #
    #     # Check if the incoming beta is the same value as the current beta
    #     if other.beta == self.beta:
    #         return type(self)(
    #             true_positives = self.true_positives + other.true_positives,
    #             false_positives = self.false_positives + other.false_positives,
    #             false_negatives = self.false_negatives + other.false_negatives,
    #             beta=self.beta,
    #         )
    #     else:
    #         raise ValueError('The "Beta" values between the two are not equal.')

    # Compute the F-Beta score metric
    def compute(self) -> jax.Array:

        # Epsilon fuz factor required to match with the keras version
        epsilon = 1e-7

        # Manually calculate precision and recall
        """
        This is done in this manner since the metrax variants of precision
        and recall output only single numbers. To match the keras value
        we need an array of numbers to work with.
        """
        precision = jnp.divide(
            self.true_positives,
            self.true_positives + self.false_positives + epsilon,
        )
        recall = jnp.divide(
            self.true_positives,
            self.true_positives + self.false_negatives + epsilon,
        )

        # Compute the numerator and denominator of the F-Score formula
        b2 = self.beta ** 2
        numerator = (1 + b2) * (precision * recall)
        denominator = (b2 * precision) + recall

        return base.divide_no_nan(
            numerator, denominator + epsilon,
        )
