from __future__ import print_function, division
import numpy as np
from sklearn.cross_validation import KFold
from sklearn.metrics import accuracy_score
from stat159lambda.classification import design_matrix as dm
from stat159lambda.classification.svm import svm
from stat159lambda.classification import partition_volumes as pv
from stat159lambda.config import REPO_HOME_PATH, NUM_VOXELS
from stat159lambda.linear_modeling import linear_modeling as lm
from stat159lambda.utils import data_path as dp


voxels_sorted_by_t_statistic = lm.VoxelExtractor(1, 'int-ext').t_stat()
# num_features_values = range(100, NUM_VOXELS/100, 100)
# for num_features in num_features_values:
voxel_feature_indices = voxels_sorted_by_t_statistic[:1000]
design_matrix = dm.DesignMatrix(dp.get_smoothed_2d_path(1, 4), pv.get_train_indices(), voxel_feature_indices)

print('classifying')
X_train = design_matrix.get_design_matrix()
y_train = np.array(design_matrix.get_labels())

cv_accuracies = []
for train, test in KFold(len(X_train), 5):
	X_cv_train = X_train[train, :]
	y_cv_train = y_train[train]
	X_cv_test = X_train[test, :]
	y_cv_test = y_train[test]
	model = svm.Classifier(X_cv_train, y_cv_train)
	model.train()
	y_predicted = model.predict(X_cv_test)
	cv_accuracies.append(accuracy_score(y_predicted, y_cv_test))

print(np.mean(cv_accuracies))
