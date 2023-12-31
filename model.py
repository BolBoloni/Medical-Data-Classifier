from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.pipeline import make_pipeline
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score

def train_and_evaluate(training_data, target_labels, categorical_columns):
    # Create a column transformer for preprocessing steps
    preprocessor = make_column_transformer(
        (OneHotEncoder(), categorical_columns),
        remainder='passthrough'
    )

    # Split the training data into training and validation set
    training_features, validation_features, training_labels, validation_labels = train_test_split(training_data, target_labels, test_size=0.4, stratify=target_labels)
    
    scale_pos_weight = len(training_labels[training_labels == 0]) / len(training_labels[training_labels == 1])
    # Create a pipeline with our preprocessor and XGBoost classifier
    model_pipeline = make_pipeline(
        preprocessor,
        XGBClassifier(n_jobs=2, learning_rate=0.01, n_estimators=1500, max_depth=14, min_child_weight=6, gamma=0.1, subsample=0.8, colsample_bytree=0.8, reg_lambda=1, reg_alpha=1, random_state=42, scale_pos_weight=scale_pos_weight)
    )

    print('Fitting model...')
    model_pipeline.fit(training_features, training_labels)
    print('Model fitted successfully')

    # Predict probabilities for the training and validation set
    # Calculate the AUC for the training and validation set
    train_predictions_proba = model_pipeline.predict_proba(training_features)[:, 1]
    validation_predictions_proba = model_pipeline.predict_proba(validation_features)[:, 1]
    train_auc_score = roc_auc_score(training_labels, train_predictions_proba)
    validation_auc_score = roc_auc_score(validation_labels, validation_predictions_proba)
    validation_predictions = model_pipeline.predict(validation_features)

    return model_pipeline, train_auc_score, validation_auc_score, validation_features, validation_labels, validation_predictions