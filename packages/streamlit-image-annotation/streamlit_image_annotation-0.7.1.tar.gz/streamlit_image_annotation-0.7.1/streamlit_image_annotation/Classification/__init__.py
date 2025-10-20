import os
import streamlit.components.v1 as components
from streamlit.components.v1.components import CustomComponent
from packaging import version

import streamlit as st
try:
    from streamlit.elements.image import image_to_url
except:
    from streamlit.elements.lib.image_utils import image_to_url

# Streamlit >= 1.49.0 uses LayoutConfig, older versions use int width
STREAMLIT_VERSION = version.parse(st.__version__)
USE_LAYOUT_CONFIG = STREAMLIT_VERSION >= version.parse("1.49.0")

if USE_LAYOUT_CONFIG:
    from streamlit.elements.lib.layout_utils import LayoutConfig

from PIL import Image
from hashlib import md5
from streamlit_image_annotation import IS_RELEASE

if IS_RELEASE:
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(absolute_path, "frontend/build")
    _component_func = components.declare_component("st_classification", path=build_path)
else:
    _component_func = components.declare_component("st_classification", url="http://localhost:3000")

def classification(image_path, label_list, default_label_index=None, height=512, width=512, key=None) -> CustomComponent:
    image = Image.open(image_path)
    image.thumbnail(size=(width, height))

    # Support both old and new Streamlit API
    if USE_LAYOUT_CONFIG:
        layout_config = LayoutConfig(width=image.size[0], height=image.size[1])
        image_url = image_to_url(image, layout_config, True, "RGB", "PNG", f"classification-{md5(image.tobytes()).hexdigest()}-{key}")
    else:
        image_url = image_to_url(image, image.size[0], True, "RGB", "PNG", f"classification-{md5(image.tobytes()).hexdigest()}-{key}")

    component_value = _component_func(image_url=image_url, image_size=image.size, label_list=label_list, default_label_idx=default_label_index, key=key)
    return component_value

if not IS_RELEASE:
    from glob import glob
    import pandas as pd
    label_list = ['deer', 'human', 'dog', 'penguin', 'framingo', 'teddy bear']
    image_path_list = glob('image/*.jpg')
    if 'result_df' not in st.session_state:
        st.session_state['result_df'] = pd.DataFrame.from_dict({'image': image_path_list, 'label': [0]*len(image_path_list)}).copy()

    num_page = st.slider('page', 0, len(image_path_list)-1, 0, key="slider")
    label = classification(image_path_list[num_page], 
                           label_list=label_list, 
                           default_label_index=int(st.session_state['result_df'].loc[num_page, 'label']),
                           key=image_path_list[num_page])

    if label is not None and label['label'] != st.session_state['result_df'].loc[num_page, 'label']:
        st.session_state['result_df'].loc[num_page, 'label'] = label_list.index(label['label'])
    st.table(st.session_state['result_df'])