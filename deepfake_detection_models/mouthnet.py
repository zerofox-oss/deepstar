import json
import pickle

from keras.optimizers import SGD
from keras import layers, models, Model
from keras.utils import multi_gpu_model
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator
from keras.applications.inception_resnet_v2 import InceptionResNetV2

# SETTINGS
GPU = 0  # Number of GPUs to use (set to 0 to use CPU)

NUM_TRAIN_SAMPLES = 23000
NUM_VALIDATION_SAMPLES = 5800
IMG_SIZE = 128

EPOCHS = 100
BATCH_SIZE = 1024
TRAINING_STEPS = int(NUM_TRAIN_SAMPLES / BATCH_SIZE)
VALIDATION_STEPS = int(NUM_VALIDATION_SAMPLES / BATCH_SIZE)

LEARNING_RATE = .1

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


# MODEL DEFINITION
base_model = InceptionResNetV2(include_top=False, weights=None, input_shape=(IMG_SIZE, IMG_SIZE, 3))

model = models.Sequential()

model.add(base_model)
model.add(layers.Flatten())

model.add(layers.Dense(128, activation='softmax', kernel_initializer='random_uniform', bias_initializer='zeros'))
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
    optimizer=SGD(lr=LEARNING_RATE, momentum=0.9, decay=LEARNING_RATE / EPOCHS),
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
        ModelCheckpoint('weights/weights.{epoch:02d}-{val_loss:.2f}.hdf5', period=3)
    ]
)

with open('training_history', 'wb') as fp:
    pickle.dump(H, fp)
with open('training_history.json', 'w') as fp:
    json.dump(H.history, fp)
model.save('final_model.hdf5')
