import json
import pickle

import keras.backend as K
from keras.optimizers import Adam
from keras import layers, models, Model
from keras.utils import multi_gpu_model
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, Callback

# SETTINGS
GPU = 0  # Number of GPUs to use (set to 0 to use CPU)

NUM_TRAIN_SAMPLES = 23000
NUM_VALIDATION_SAMPLES = 5800
IMG_SIZE = 256

EPOCHS = 1000
BATCH_SIZE = 75
TRAINING_STEPS = int(NUM_TRAIN_SAMPLES / BATCH_SIZE)
VALIDATION_STEPS = int(NUM_VALIDATION_SAMPLES / BATCH_SIZE)

LEARNING_RATE = 1e-3

TRAIN_DATA_DIR = 'dataset/train'
VALIDATION_DATA_DIR = 'dataset/test'


class ModelMGPU(Model):
    def __init__(self, ser_model, gpus):
        pmodel = multi_gpu_model(ser_model, gpus)
        self.__dict__.update(pmodel.__dict__)
        self._smodel = ser_model

    def __getattribute__(self, attrname):
        """
        Override load and save methods to be used from the serial-model.
        The serial-model holds references to the weights in the multi-gpu model.
        """

        if 'load' in attrname or 'save' in attrname:
            return getattr(self._smodel, attrname)
        else:
            return super(ModelMGPU, self).__getattribute__(attrname)


class LRStepScheduler(Callback):
    """
    Basic step scheduler as implemented by the MesoNet authors.
    """

    def __init__(self, max_lr=1e-3, min_lr=1e-6, num_iter=1000, divisor=10):
        self.max_lr = max_lr
        self.min_lr = min_lr
        self.num_iter = num_iter
        self.divisor = divisor
        self.iter_count = 0
        self.cur_lr = max_lr
        self.history = {}
    
    def on_train_begin(self, logs={}):
        logs = logs or {}
        K.set_value(self.model.optimizer.lr, self.max_lr)

    def on_batch_end(self, batch, logs={}):
        logs = logs or {}
        self.history.setdefault('lr', []).append(K.get_value(self.model.optimizer.lr))

        self.iter_count += 1
        if self.iter_count % self.num_iter == 0:
            self.cur_lr = self.cur_lr / self.divisor
            if self.cur_lr < self.min_lr:
                self.cur_lr = self.min_lr
            K.set_value(self.model.optimizer.lr, self.cur_lr)


# MODEL DEFINITION
model = models.Sequential()
model.add(layers.Conv2D(8, (3, 3), padding='same', activation='relu', data_format='channels_last',
                        input_shape=(IMG_SIZE, IMG_SIZE, 3)))
model.add(layers.BatchNormalization(axis=3))
model.add(layers.MaxPooling2D())

model.add(layers.Conv2D(8, (5, 5), padding='same', activation='relu', data_format='channels_last'))
model.add(layers.BatchNormalization(axis=3))
model.add(layers.MaxPooling2D())

model.add(layers.Conv2D(16, (5, 5), padding='same', activation='relu', data_format='channels_last'))
model.add(layers.BatchNormalization(axis=3))
model.add(layers.MaxPooling2D())

model.add(layers.Conv2D(16, (5, 5), padding='same', activation='relu', data_format='channels_last'))
model.add(layers.BatchNormalization(axis=3))
model.add(layers.MaxPooling2D(pool_size=(4, 4)))

model.add(layers.Flatten())
model.add(layers.Dropout(0.5))
model.add(layers.Dense(16, activation='linear', kernel_initializer='random_uniform', bias_initializer='zeros'))

model.add(layers.Dropout(0.5))
model.add(layers.Dense(1, activation='sigmoid', kernel_initializer='random_uniform', bias_initializer='zeros'))

model.summary()

# TRAINING SETUP
if GPU > 0:
    run_model = ModelMGPU(model, GPU)
    run_model.summary()
else:
    run_model = model

run_model.compile(
    loss="binary_crossentropy",
    optimizer=Adam(),
    metrics=["accuracy"]
)

train_datagen = ImageDataGenerator(
    samplewise_center=False,
    samplewise_std_normalization=True,
    zoom_range=0.2,
    brightness_range=(.6, 1.4),
    rotation_range=45,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    data_format='channels_last',
)

validation_datagen = ImageDataGenerator(
    samplewise_center=False,
    samplewise_std_normalization=True,
    data_format='channels_last',
)

train_generator = train_datagen.flow_from_directory(
    TRAIN_DATA_DIR,
    classes=['real', 'deepfake'],
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary')

validation_generator = validation_datagen.flow_from_directory(
    VALIDATION_DATA_DIR,
    classes=['real', 'deepfake'],
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='binary')

H = run_model.fit_generator(
    train_generator,
    steps_per_epoch=TRAINING_STEPS,
    epochs=EPOCHS,
    validation_data=validation_generator,
    validation_steps=VALIDATION_STEPS,
    verbose=2,
    workers=8,
    use_multiprocessing=False,
    callbacks=[
        ModelCheckpoint('weights/weights.{epoch:02d}-{val_loss:.2f}.hdf5', period=3),
        LRStepScheduler(),
    ]
)

with open('training_history', 'wb') as fp:
    pickle.dump(H, fp)
with open('training_history.json', 'w') as fp:
    json.dump(H.history, fp)
model.save('final_model.hdf5')
