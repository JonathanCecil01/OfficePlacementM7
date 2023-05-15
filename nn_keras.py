import tensorflow as tf

model = tf.keras.models.load_model('nn_time_range')


print(model.summary())

