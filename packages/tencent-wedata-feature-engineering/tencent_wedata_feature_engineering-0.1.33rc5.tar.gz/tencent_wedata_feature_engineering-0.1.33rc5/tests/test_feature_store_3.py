from datetime import datetime
import pandas as pd
import mlflow

best_model = mlflow.pyfunc.load_model(f"models:/david_11111/2")

# 1. 把 timestamp 也当成特征
feature_columns = ['fixed_acidity', 'volatile_acidity', 'citric_acid',
                   'residual_sugar', 'chlorides', 'free_sulfur_dioxide',
                   'total_sulfur_dioxide', 'density', 'pH', 'sulphates',
                   'alcohol', 'event_timestamp']

new_data = pd.DataFrame([
    (7.4, 0.7, 0.0, 1.9, 0.076, 11, 34, 0.9978, 3.51, 0.56, 9.4,
     int(datetime(2025, 10, 1).timestamp())),
    (7.8, 0.58, 0.02, 2.0, 0.073, 9, 18, 0.9968, 3.36, 0.57, 9.5,
     int(datetime(2025, 10, 2).timestamp()))
], columns=feature_columns)

# 2. 保持与训练时完全一致的 dtype
new_data['free_sulfur_dioxide']  = new_data['free_sulfur_dioxide'].astype('int32')
new_data['total_sulfur_dioxide'] = new_data['total_sulfur_dioxide'].astype('int32')
new_data['event_timestamp']      = new_data['event_timestamp'].astype('int64')

prediction = best_model.predict(new_data)
print(f"\n红酒质量的预测结果: {prediction}")