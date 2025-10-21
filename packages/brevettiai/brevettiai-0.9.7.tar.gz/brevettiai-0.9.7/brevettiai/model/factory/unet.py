from tensorflow.keras import layers
import tensorflow as tf

from brevettiai.model.factory import ModelFactory

class UnetSegmentationHead(ModelFactory):
    decoder_filters = (256, 128, 64, 32, 16)
    n_upsample_blocks = 5
    classes = 4
    activation = 'sigmoid'
    bn_momentum = 0.99

    def build(self, input_shape, output_shape, **kwargs):
        input_channels = [i[-1] for i in input_shape][::-1]
        inp = layers.Input((None, None, input_channels[0]))
        skip_connection_layers = [layers.Input((None, None, i)) for i in input_channels[1:]]

        x = inp
        for i in range(self.n_upsample_blocks):
            print(x.shape)
            skip = skip_connection_layers[i] if i < len(skip_connection_layers) else None
            x = self._decode_upsample(x, skip, self.decoder_filters[i], id=i, batch_norm_momentum=self.bn_momentum)
        print(x.shape)
        x = layers.Conv2D(output_shape[-1], kernel_size=(3, 3), padding="same")(x)

        model = tf.keras.Model([inp, *skip_connection_layers][::-1], x)
        return model


    def _decode_upsample_add(self, x, skip, skip_filter, batch_norm_momentum=0.99, id=None):
        filter = x.shape[-1]
        x = self._conv_block(x, filter // 4, (1, 1), batch_norm_momentum, name="upsample_conv1_" + str(id))

        x = layers.UpSampling2D(size=2, name="upsample_" + str(id))(x)

        x = self._conv_block(x, filter // 4, (3, 3), batch_norm_momentum, name="upsample_conv2_" + str(id))
        x = self._conv_block(x, skip_filter, (1, 1), batch_norm_momentum, name="upsample_conv3_" + str(id))

        if skip is not None:
            x = layers.Add()([x, skip])
        return x

    def _conv_block(self, x, filters, kernel, batch_norm_momentum=None, **kwargs):
        x = layers.Conv2D(filters, kernel, padding="same")(x)
        if batch_norm_momentum:
            x = layers.BatchNormalization(momentum=batch_norm_momentum)(x)
        x = layers.Activation("relu")(x)
        return x


    def _decode_upsample(self, x, skip, filters, concat_axis=-1, batch_norm_momentum=0.99, id=None):
        x = layers.UpSampling2D(size=2, name="upsample_" + str(id))(x)

        if skip is not None:
            x = layers.Concatenate(axis=concat_axis, name="upsample_concat_" + str(id))([x, skip])

        x = self._conv_block(x, filters, (3, 3), batch_norm_momentum, name="upsample_conv1_" + str(id))
        x = self._conv_block(x, filters, (3, 3), batch_norm_momentum, name="upsample_conv2_" + str(id))

        return x
