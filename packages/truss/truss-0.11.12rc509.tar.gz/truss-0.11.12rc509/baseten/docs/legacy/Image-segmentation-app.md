
## Deploy the image segmentation model
In `shell_plus`, run the following code:
```python
# See faster_rcnn_inception_v2.py for details on the model.
from oracles.model_zoo.shared_models import create_pretrained_model_for_user
create_pretrained_model_for_user('faster_rcnn_inception_v2', u)  # Be sure u=the user you want to associate the model with.
```


## Create an application for the model

### Worklet

```
py1 -> ImageToArray -> Invoke model -> py2
```

The `py1` node just unpacks the `image_data` key from an input dict (as the front-end can only submit data as key-value pairs for now). The `image_data` value is either a url or a base64 encoded image.

```python
def py1(node_input, state, context):
    return node_input['image_data']
```

`ImageToArray` converts the data into an array of rgb values.

The `py2` node takes the model output and processes it into a format consumable by the image segmentation front end element.

```python
def process_model_output(node_input, state, context):
  """This node will execute the code that you provide below.
          context: Provides readonly access to contextual information such as user id.
                   Provides helper methods, e.g. to run queries.
                   Please refer to [TODO - docs link] for details.
       node_input: Input to this node. Should be Json Serializable.
       state: Mutable State that is threaded through the worklet. Modify it like a dictionary.             Should be Json Serializable.
  """
  predictions = node_input['predictions'][0]
  boxes = predictions['detection_boxes']
  classes = predictions['detection_classes']
  scores = predictions['detection_scores']
  num_detections = predictions['num_detections']
  bounding_boxes = []
  for detection in range(int(num_detections)):
    bbox = {
      'top': boxes[detection][0],
      'left': boxes[detection][1],
      'bottom': boxes[detection][2],
      'right': boxes[detection][3],
      'score': round(100*scores[detection]),
      'class': classes[detection]
    }
    bounding_boxes.append(bbox)
  return bounding_boxes
  ```

### View

- Create image_segmenter
    - src: an image
    - boundingBoxes: `{{ context.worklets.theworklet ? context.worklets.theworklet.output : [] }}`
- Create a button
    - onClick: run worklet: theworklet
    - parameterName: image_data
    - parameterValue `{{ components.image_segmenter_1.src.value }}`

## Run the app with some images

