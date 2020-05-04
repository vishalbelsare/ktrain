# Frequently Asked Questions About `ktrain`

- [I am a newcomer and am having trouble figuring out how to even to even get started. Where do I begin?](#i-am-a-newcomer-and-am-having-trouble-figuring-out-how-to-even-get-started-where-do-i-begin)

- [How do I obtain the word or sentence embeddings after fine-tuning a Transformer-based text classifier?](#how-do-i-obtain-the-word-or-sentence-embeddings-after-fine-tuning-a-transformer-based-text-classifier)

- [How do I train using multiple GPUs?](#how-do-i-train-using-multiple-gpus)

- [How do I train a model using mixed precision?](#how-do-i-train-a-model-using-mixed-precision)

- [How do I deploy a model using Flask?](#how-do-i-deploy-a-model-using-flask)

- [How do I use custom metrics with ktrain?](#how-do-i-use-custom-metrics-with-ktrain)

- [How do I get the predicted class "probabilities" of a model?](#how-do-i-get-the-predicted-class-probabilities-of-a-model)

- [How do I retrieve or visualize training history?](#how-do-i-retrieve-or-visualize-training-history)

- [I have a model that accepts multiple inputs (e.g., both text and other numerical or categorical variables).  How do train it with *ktrain*?](#i-have-a-model-that-accepts-multiple-inputs-eg-both-text-and-other-numerical-or-categorical-variables--how-do-train-it-with-ktrain)


### I am a newcomer and am having trouble figuring out how to even get started. Where do I begin?

Machine learning models (e.g., neural networks) are trained on example inputs and outputs to learn mappings between them.  Once trained, given a new input, a correct output can be predicted.
For example, if you train a neural network on documents (i.e., inputs) and document categories or topics (i.e, outputs), the neural network will learn to predict the categories of new documents.  
Training neural network models can be computationally intensive due to the number of mathematical operations it takes to learn the mappings.  GPUs (or Graphical Processing Units) are devices
that allow you train neural networks faster by performing many mathematical operations at the same time. 

*ktrain* is a Python library that allows you train a neural network and make predictions using a minimal number of "commands" or lines of code. 
It is built on top of a library by Google called TensorFlow. Only limited Python knowledge is required to use it.  


The three biggest challenges for newcomers are gaining access to a computer with a GPU, installing and setting up the TensorFlow library to use the GPU, and setting up Jupyter notebook.
(Jupyter notebook are programming environemnts that allow you to interactively type code and see and save results of that code in an interacive fashion.)  
Fortunately, Google did a nice thing and made notebook environments with GPU access freely available "in the cloud" to anyone with a Gmail account.

Here is how you can quickly get started using *ktrain*:

1. Go to the [Google Colab](https://colab.research.google.com/notebooks/intro.ipynb) and sign in using your Gmail account.
2. Go to this [example notebook on image classification](https://colab.research.google.com/drive/1WipQJUPL7zqyvLT10yekxf_HNMXDDtyR). This notebook shows you how to build a neural network that recoginizes cats vs. dogs in photos.
3. Save the notebook to your Google Drive: `File --> Save a copy in Drive`
4. Make sure the notebook is setup to use a GPU: `Runtime --> Change runtime type` and select `GPU` in the menu.
5. Click on each cell in the notebook and execute it by pressing `SHIFT` and `ENTER` at the same time.


- For more information on `ktrain`, see [the tutorials](https://github.com/amaiya/ktrain#tutorials).

- For more information on Python, see [here](https://learnpythonthehardway.org/).

- For more information on neural networks, see [this page](https://victorzhou.com/blog/intro-to-neural-networks/).

- For more information on Google Colab, see [this video](https://www.youtube.com/watch?v=inN8seMm7UI).

- For more information on Jupyter notebooks, see [this video](https://www.youtube.com/watch?v=HW29067qVWk).


### How do I obtain the word or sentence embeddings after fine-tuning a Transformer-based text classifier?
Here is a self-contained example of generating word embeddings from a fine-tuned `Transformer` model:

```python
# load text data
categories = ['alt.atheism', 'soc.religion.christian','comp.graphics', 'sci.med']
from sklearn.datasets import fetch_20newsgroups
train_b = fetch_20newsgroups(subset='train', categories=categories, shuffle=True)
test_b = fetch_20newsgroups(subset='test',categories=categories, shuffle=True)
(x_train, y_train) = (train_b.data, train_b.target)
(x_test, y_test) = (test_b.data, test_b.target)

# build, train, and validate model (Transformer is wrapper around transformers library)
import ktrain
from ktrain import text
MODEL_NAME = 'distilbert-base-uncased'
t = text.Transformer(MODEL_NAME, maxlen=500, class_names=train_b.target_names)
trn = t.preprocess_train(x_train, y_train)
val = t.preprocess_test(x_test, y_test)
model = t.get_classifier()
learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=6)
learner.fit_onecycle(5e-5, 1)

# load model to generate embeddingsmodel.save_pretrained('/tmp/mymodel')
from transformers import *
import tensorflow as tf
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = TFAutoModel.from_pretrained('/tmp/mymodel')
input_ids = tf.constant(tokenizer.encode("Hello, my dog is cute"))[None, :]  # Batch size 1
outputs = model(input_ids)
last_hidden_states = outputs[0]  # The last hidden-state is the first element of the output tuple
print(last_hidden_states.numpy().shape)  # print shape of embedding vectors
```
This will produce a vector for each word (and subword) in the input string.  For sentence embeddings, you can aggregate
in various ways (e.g., average vectors).

See also [this post](https://github.com/huggingface/transformers/issues/1950) on the `transformers` GitHub repo.

[[Back to Top](#frequently-asked-questions-about-ktrain)]



### How do I train using multiple GPUs?

Since *ktrain* is just a simple wrapper around TensorFlow,  you can use multiple GPUs in the same way you would for a normal `tf.Keras` model.
Here is a fully-complete, self-contained example for using 2 GPUs with a `Transformer` model:

```python
# use two GPUs to train
import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID";
os.environ["CUDA_VISIBLE_DEVICES"]="0,1";  

# load text data
categories = ['alt.atheism', 'soc.religion.christian','comp.graphics', 'sci.med']
from sklearn.datasets import fetch_20newsgroups
train_b = fetch_20newsgroups(subset='train', categories=categories, shuffle=True)
test_b = fetch_20newsgroups(subset='test',categories=categories, shuffle=True)
(x_train, y_train) = (train_b.data, train_b.target)
(x_test, y_test) = (test_b.data, test_b.target)

# build, train, and validate model
import tensorflow as tf
mirrored_strategy = tf.distribute.MirroredStrategy()
import ktrain
from ktrain import text
MODEL_NAME = 'distilbert-base-uncased'
t = text.Transformer(MODEL_NAME, maxlen=500, class_names=train_b.target_names)
trn = t.preprocess_train(x_train, y_train)
val = t.preprocess_test(x_test, y_test)
with mirrored_strategy.scope():
    model = t.get_classifier()
learner = ktrain.get_learner(model, train_data=trn, batch_size=6)
learner.fit_onecycle(5e-5, 2)
learner.save_model('/tmp/my_model')
learner.load_model('/tmp/my_model', preproc=t)
learner.validate(val_data=val, class_names=t.get_classes())
```

[[Back to Top](#frequently-asked-questions-about-ktrain)]



### How do I train a model using mixed precision?

See [this post](https://github.com/amaiya/ktrain/issues/126#issuecomment-616545655).


[[Back to Top](#frequently-asked-questions-about-ktrain)]


### How do I deploy a model using Flask?

See [this post](https://github.com/amaiya/ktrain/issues/37#issuecomment-568085054).

[[Back to Top](#frequently-asked-questions-about-ktrain)]

### How do I use custom metrics with *ktrain*?
You can use custom callbacks:

```python
# define a custom callback for ROC-AUC
from tensorflow.keras.callbacks import Callback
from sklearn.metrics import roc_auc_score
class RocAucEvaluation(Callback):
    def __init__(self, validation_data=(), interval=1):
        super(Callback, self).__init__()

        self.interval = interval
        self.X_val, self.y_val = validation_data

    def on_epoch_end(self, epoch, logs={}):
        if epoch % self.interval == 0:
            y_pred = self.model.predict(self.X_val, verbose=0)
            score = roc_auc_score(self.y_val, y_pred)
            print("\n ROC-AUC - epoch: %d - score: %.6f \n" % (epoch+1, score))
RocAuc = RocAucEvaluation(validation_data=(x_test, y_test), interval=1)

# train using our custom ROC-AUC callback
learner = ktrain.get_learner(model, train_data=train_data, val_data = val_data)
learner.autofit(0.005, 2, callbacks=[RocAuc])
```

[[Back to Top](#frequently-asked-questions-about-ktrain)]

### How do I get the predicted class "probabilities" of a model?

All `predict` methods in `Predictor` instances accept a `return_proba` argument.  Set it to true to obtain the class probabilities.


[[Back to Top](#frequently-asked-questions-about-ktrain)]


### How do I retrieve or visualize training history?

As with normal `tf.Keras` models, all `*fit*` methods in *ktrain* return the training history data.
```python
history = learner.autofit(...)
```

To visualize the training and validation loss by epochs:
```python
learner.plot('loss')
```

To visualize the learning rate schedule, you can do this:
```python
learner.plot('lr')
```

[[Back to Top](#frequently-asked-questions-about-ktrain)]

### I have a model that accepts multiple inputs (e.g., both text and other numerical or categorical variables).  How do train it with *ktrain*?

See [this tutorial](https://nbviewer.jupyter.org/github/amaiya/ktrain/blob/master/tutorials/tutorial-A4-customdata-text_regression_with_extra_regressors.ipynb).


[[Back to Top](#frequently-asked-questions-about-ktrain)]
