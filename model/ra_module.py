'''
MIT License

Copyright (c) 2020 Tauhid Khan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from conv_module import ConvModule
import tensorflow as tf


class ReverseAttention(tf.keras.layers.Layer):
    def __init__(self, filters: int = 64, kernel_size: tuple = (3, 3), **kwargs):
        super(ReverseAttention, self).__init__(**kwargs)
        self.filters = filters
        self.kernel_size = kernel_size

        self.conv1 = ConvModule(filters=self.filters, kernel_size=(1, 1))
        self.conv2 = ConvModule(filters=self.filters,
                                kernel_size=self.kernel_size)
        self.conv3 = ConvModule(filters=self.filters,
                                kernel_size=self.kernel_size)
        self.conv4 = ConvModule(filters=1, kernel_size=self.kernel_size)

    def call(self, side_feat: tf.Tensor, saliency_m: tf.Tensor) -> tf.Tensor:
        prev_sm = saliency_m
        x = tf.sigmoid(prev_sm)
        x = -1*(x)+1
        x = tf.math.multiply(x, side_feat)

        x = self.conv1(x)
        x = tf.nn.relu(self.conv2(x))
        x = tf.nn.relu(self.conv3(x))
        ra_feat = self.conv4(x)

        ra_feat = ra_feat + saliency_m

        return ra_feat

    def get_config(self) -> dict:
        config = super().get_config()
        config.update({
            "filters": self.filters,
            "kernel_size": self.kernel_size
        })

        return config

    @classmethod
    def from_config(cls, **config):
        return super().from_config(**config)


if __name__ == "__main__":
    ra = ReverseAttention(filters=64, kernel_size=(3, 3))
    # first call to the `ra` will create weights

    sm = tf.ones(shape=(8, 44, 44, 1))
    side_feat = tf.ones(shape=(8, 11, 11, 2048))
    resized_side_feat = tf.keras.layers.experimental.preprocessing.Resizing(
        sm.shape[1], sm.shape[2])(side_feat)
    print(f"shape of resize feat: {resized_side_feat.shape}")
    y = ra(resized_side_feat, sm)

    print("weights:", len(ra.weights))
    print("trainable weights:", len(ra.trainable_weights))
    print("config:", ra.get_config())
    print(f"Y: {y.shape}")
