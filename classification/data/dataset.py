import os
import glob
import trimesh
import pymeshlab
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from tqdm import tqdm
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot as plt

# tf.random.set_seed(1234)

### Global Constants ###
mesh_set = pymeshlab.MeshSet()
data_dir = Path(__file__).parent.absolute()
segment_labels = pd.read_csv(f"{data_dir}/segment_labels.csv")
colors = [[1, 1, 1, 1], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 0.8, 1, 1], [1, 0.1, 0.6, 1], [1, 0.647, 0, 1], [0.5, 0.647, 0, 1], [1, 0.647, 0.5, 1], [0.5, 0.647, 0.5, 1], [0.5, 0.5, 0.2, 1], [0.1, 0.8, 0.1, 1], [0.9, 0.1, 0.5, 1], [0.2, 0.1, 0.9, 1], [0.8, 0.8, 0.1, 1], [0.843, 0.6423, 0.123, 1], [0.8123, 0.2423, 0.654, 1], [0.75, 0.63, 0.3, 1], [0.912, 0.36, 0.18, 1]]
models = {f"model_{i}": [0]*12 for i in [3, 4, 6, 16, 18, 20, 21, 22, 26, 31, 32, 34, 35, 36, 38, 40, 41, 44, 45, 47, 51, 57, 59, 62, 63, 64, 66, 68, 74, 75, 77, 81, 82, 83, 84, 86, 87, 88, 91, 92, 93, 95, 96, 97]}

def parse_dataset(num_points = 2048):
    class_map = {}
    test_points = []
    test_labels = []
    train_points = []
    train_labels = []
    non_existing = {"model_96", "model_34", "model_66", "model_74", "model_15", "model_86", "model_57", "model_62", "model_95"}

    for i, row in segment_labels.iterrows():
            try: model_number = int(row['model'])
            except: continue
            if f"model_{model_number}" in non_existing: continue

            segment = int(row['segment'])

            label = row['label']
            models[f"model_{model_number}"][segment] = 0 if label == "Form" else 1

    j = -1
    k = 0
    for model_name, labels in tqdm(models.items(), total=40):
        if model_name in non_existing: continue 
        # print(f"processing {model_name}")
        for i, label in enumerate(labels):
            if j <= 30:
                train_points.append(trimesh.load(f"{data_dir}/segments/{model_name}/{i}.obj").sample(num_points))
                train_labels.append(label)
            else:
                test_points.append(trimesh.load(f"{data_dir}/segments/{model_name}/{i}.obj").sample(num_points))
                test_labels.append(label)
            class_map[k] = label
            k += 1
        j += 1
        
    print(f"Training: {len(train_points)}")
    print(f"Testing: {len(test_points)}")

    return (
        np.array(train_points),
        np.array(test_points),
        np.array(train_labels),
        np.array(test_labels),
        class_map,
    )

def _get_submesh(mesh_path, j):
    colors_to_faces = {}
    try:
        all_vertices = []
        with open(mesh_path, "r") as mesh:
            for line in mesh.readlines():
                if line.startswith("v "):
                    line_ = line.split(" ")[1:]
                    x, y, z, = list(map(float, line_[:3]))
                    all_vertices.append([x, y, z])

        with open(mesh_path, "r") as mesh:
            for line in mesh.readlines():
                if line.startswith("usemtl "):
                    color = int(line.split(" ")[1].split("_")[1])

                if line.startswith("f "):
                    line_ = line.strip().split(" ")[1:]
                    try: colors_to_faces[color].append(list(map(lambda x: int(x.split("//")[0]) - 1, line_)))
                    except: colors_to_faces[color] = [list(map(lambda x: int(x.split("//")[0]) - 1, line_))]
        
        i = 0
        faces = []
        v_to_i = {}
        vertices = []
        history = set()
        for face in colors_to_faces[j]:
            for v in face:
                if v >= len(all_vertices): raise ValueError(f"Face vertex index {v} > len(vertices) = {len(all_vertices)}")
                if v not in history: 
                    vertices.append(all_vertices[v])
                    history.add(v)
                    v_to_i[v] = i
                    i += 1
            faces.append(list(map(lambda v: v_to_i[v], face)))
            
    except IndexError as error: print(f"Vertex {v} could not be found in vertices of length {len(all_vertices)}")
    except Exception as error: raise error; print(f"Could not find {mesh_path}\n----\n{error}\n----"); return [], []
    return np.array(vertices), np.array(faces)
  
if __name__ == "__main__":
    # non_existing = {96, 34, 66, 74, 15, 86, 57, 62, 95}
    # print(f"Labeled: {len(models) - len(non_existing)}")
    # for i, row in segment_labels.iterrows():
    #     try: model_number = int(row['model'])
    #     except: continue
    #     if model_number in non_existing: continue

    #     segment = int(row['segment'])

    #     label = row['label']
    #     try:
    #         vertices, faces = _get_submesh(f"{data_dir}/Segmented_Models/model_{model_number}/model_{model_number}_segmented_new.obj", segment)
    #         print(f"Model {model_number}\n\tsegment {segment}\n\tvertices {len(vertices)}\n\tfaces {len(faces)}")
    #         models[f"model_{model_number}"][segment] = label

    #         try: os.mkdir(f"{data_dir}/segments/model_{model_number}")
    #         except: None

    #         if len(faces) > 1: 
    #             mesh_set.add_mesh(pymeshlab.Mesh(vertices, faces))
    #             mesh_set.save_current_mesh(f"{data_dir}/segments/model_{model_number}/{segment}.obj")
    #     except Exception as error: non_existing.add(model_number)
    NUM_POINTS = 2048
    NUM_CLASSES = 2
    BATCH_SIZE = 1

    train_points, test_points, train_labels, test_labels, CLASS_MAP = parse_dataset(NUM_POINTS)

    def augment(points, label):
        # jitter points
        points += tf.random.uniform(points.shape, -0.005, 0.005, dtype=tf.float64)
        # shuffle points
        points = tf.random.shuffle(points)
        return points, label

    train_dataset = tf.data.Dataset.from_tensor_slices((train_points, train_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_points, test_labels))

    train_dataset = train_dataset.shuffle(len(train_points)).map(augment).batch(BATCH_SIZE)
    test_dataset = test_dataset.shuffle(len(test_points)).batch(BATCH_SIZE)

    def conv_bn(x, filters):
        x = layers.Conv1D(filters, kernel_size=1, padding="valid")(x)
        x = layers.BatchNormalization(momentum=0.0)(x)
        return layers.Activation("relu")(x)


    def dense_bn(x, filters):
        x = layers.Dense(filters)(x)
        x = layers.BatchNormalization(momentum=0.0)(x)
        return layers.Activation("relu")(x)
    
    class OrthogonalRegularizer(keras.regularizers.Regularizer):
        def __init__(self, num_features, l2reg=0.001):
            self.num_features = num_features
            self.l2reg = l2reg
            self.eye = tf.eye(num_features)

        def __call__(self, x):
            x = tf.reshape(x, (-1, self.num_features, self.num_features))
            xxt = tf.tensordot(x, x, axes=(2, 2))
            xxt = tf.reshape(xxt, (-1, self.num_features, self.num_features))
            return tf.reduce_sum(self.l2reg * tf.square(xxt - self.eye))
    
    def tnet(inputs, num_features):

        # Initalise bias as the indentity matrix
        bias = keras.initializers.Constant(np.eye(num_features).flatten())
        reg = OrthogonalRegularizer(num_features)

        x = conv_bn(inputs, 32)
        x = conv_bn(x, 64)
        x = conv_bn(x, 512)
        x = layers.GlobalMaxPooling1D()(x)
        x = dense_bn(x, 256)
        x = dense_bn(x, 128)
        x = layers.Dense(
            num_features * num_features,
            kernel_initializer="zeros",
            bias_initializer=bias,
            activity_regularizer=reg,
        )(x)
        feat_T = layers.Reshape((num_features, num_features))(x)
        # Apply affine transformation to input features
        return layers.Dot(axes=(2, 1))([inputs, feat_T])
    

    inputs = keras.Input(shape=(NUM_POINTS, 3))

    x = tnet(inputs, 3)
    x = conv_bn(x, 32)
    x = conv_bn(x, 32)
    x = tnet(x, 32)
    x = conv_bn(x, 32)
    x = conv_bn(x, 64)
    x = conv_bn(x, 512)
    x = layers.GlobalMaxPooling1D()(x)
    x = dense_bn(x, 256)
    x = layers.Dropout(0.3)(x)
    x = dense_bn(x, 128)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs, name="pointnet")
    model.summary()

    model.compile(
        loss="sparse_categorical_crossentropy",
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        metrics=["sparse_categorical_accuracy"],
    )

    model.fit(train_dataset, epochs=20, validation_data=test_dataset)
    
    data = test_dataset.take(1)

    points, labels = list(data)[0]
    points = points[:8, ...]
    labels = labels[:8, ...]
    
    # run test data through model
    preds = model.predict(points)
    preds = tf.math.argmax(preds, -1)

    points = points.numpy()
    
    print(points.shape)
    # plot points with predicted class and label
    for i in range(1):
       print("pred: {:}, label: {:}".format(
                CLASS_MAP[preds[i].numpy()], CLASS_MAP[labels.numpy()[i]]
            )
        )
