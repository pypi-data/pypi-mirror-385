
import gradio as gr
from app import demo as app
import os

_docs = {'ImageMeta': {'description': "A Gradio component for uploading or displaying images, with support for metadata extraction and a custom load_metadata event.\n\nThis component allows users to upload images (as input) or display images (as output). It includes a custom event for loading metadata, triggered by a 'Load Metadata' button in the UI, which expects ImageMetaData as input.", 'members': {'__init__': {'value': {'type': 'str | Image.Image | np.ndarray | Callable | None', 'default': 'None', 'description': 'A PIL Image, numpy array, path or URL for the default value that Image component is going to take. If a function is provided, the function will be called each time the app loads to set the initial value of this component.'}, 'format': {'type': 'str', 'default': '"webp"', 'description': 'File format (e.g. "png" or "gif"). Used to save image if it does not already have a valid format (e.g. if the image is being returned to the frontend as a numpy array or PIL Image). The format should be supported by the PIL library. Applies both when this component is used as an input or output. This parameter has no effect on SVG files.'}, 'height': {'type': 'int | str | None', 'default': 'None', 'description': 'The height of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.'}, 'width': {'type': 'int | str | None', 'default': 'None', 'description': 'The width of the component, specified in pixels if a number is passed, or in CSS units if a string is passed. This has no effect on the preprocessed image file or numpy array, but will affect the displayed image.'}, 'image_mode': {'type': 'Literal[\n        "1",\n        "L",\n        "P",\n        "RGB",\n        "RGBA",\n        "CMYK",\n        "YCbCr",\n        "LAB",\n        "HSV",\n        "I",\n        "F",\n    ]\n    | None', 'default': '"RGB"', 'description': 'The pixel format and color depth that the image should be loaded and preprocessed as. "RGB" will load the image as a color image, or "L" as black-and-white. See https://pillow.readthedocs.io/en/stable/handbook/concepts.html for other supported image modes and their meaning. This parameter has no effect on SVG or GIF files. If set to None, the image_mode will be inferred from the image file type (e.g. "RGBA" for a .png image, "RGB" in most other cases).'}, 'type': {'type': 'Literal["numpy", "pil", "filepath"]', 'default': '"numpy"', 'description': 'The format the image is converted before being passed into the prediction function. "numpy" converts the image to a numpy array with shape (height, width, 3) and values from 0 to 255, "pil" converts the image to a PIL image object, "filepath" passes a str path to a temporary file containing the image. To support animated GIFs in input, the `type` should be set to "filepath" or "pil". To support SVGs, the `type` should be set to "filepath".'}, 'label': {'type': 'str | I18nData | None', 'default': 'None', 'description': 'The label for this component. Appears above the component and is also used as the header if there are a table of examples for this component. If None and used in a `gr.Interface`, the label will be the name of the parameter this component is assigned to.'}, 'every': {'type': 'Timer | float | None', 'default': 'None', 'description': 'Continously calls `value` to recalculate it if `value` is a function (has no effect otherwise). Can provide a Timer whose tick resets `value`, or a float that provides the regular interval for the reset Timer.'}, 'inputs': {'type': 'Component | Sequence[Component] | set[Component] | None', 'default': 'None', 'description': 'Components that are used as inputs to calculate `value` if `value` is a function (has no effect otherwise). `value` is recalculated any time the inputs change.'}, 'show_label': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will display label.'}, 'show_download_button': {'type': 'bool', 'default': 'True', 'description': 'If True, will display button to download image. Only applies if interactive is False (e.g. if the component is used as an output).'}, 'container': {'type': 'bool', 'default': 'True', 'description': 'If True, will place the component in a container - providing some extra padding around the border.'}, 'scale': {'type': 'int | None', 'default': 'None', 'description': 'Relative size compared to adjacent Components. For example if Components A and B are in a Row, and A has scale=2, and B has scale=1, A will be twice as wide as B. Should be an integer. scale applies in Rows, and to top-level Components in Blocks where fill_height=True.'}, 'min_width': {'type': 'int', 'default': '160', 'description': 'Minimum pixel width, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in this Component being narrower than min_width, the min_width parameter will be respected first.'}, 'interactive': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will allow users to upload and edit an image; if False, can only be used to display images. If not provided, this is inferred based on whether the component is used as an input or output.'}, 'visible': {'type': 'bool', 'default': 'True', 'description': 'If False, component will be hidden.'}, 'elem_id': {'type': 'str | None', 'default': 'None', 'description': 'An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'elem_classes': {'type': 'list[str] | str | None', 'default': 'None', 'description': 'An optional list of strings that are assigned as the classes of this component in the HTML DOM. Can be used for targeting CSS styles.'}, 'render': {'type': 'bool', 'default': 'True', 'description': 'If False, component will not render be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.'}, 'key': {'type': 'int | str | tuple[int | str, ...] | None', 'default': 'None', 'description': "In a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render."}, 'preserved_by_key': {'type': 'list[str] | str | None', 'default': '"value"', 'description': "A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor."}, 'show_share_button': {'type': 'bool | None', 'default': 'None', 'description': 'If True, will show a share icon in the corner of the component that allows user to share outputs to Hugging Face Spaces Discussions. If False, icon does not appear. If set to None (default behavior), then the icon appears if this Gradio app is launched on Spaces, but not otherwise.'}, 'placeholder': {'type': 'str | None', 'default': 'None', 'description': 'Custom text for the upload area. Overrides default upload messages when provided. Accepts new lines and `#` to designate a heading.'}, 'show_fullscreen_button': {'type': 'bool', 'default': 'True', 'description': 'If True, will show a fullscreen icon in the corner of the component that allows user to view the image in fullscreen mode. If False, icon does not appear.'}, 'only_custom_metadata': {'type': 'bool', 'default': 'True', 'description': 'If True, extracts only custom metadata, excluding technical metadata like ImageWidth or ImageHeight. Defaults to True.'}, 'disable_preprocess': {'type': 'bool', 'default': 'True', 'description': 'If True, skips preprocessing and returns the raw ImageMetaData payload. Defaults to True.'}, 'popup_metadata_width': {'type': 'int | str', 'default': '400', 'description': 'Metadata popup width in pixels or CSS units. Defaults to 400.'}, 'popup_metadata_height': {'type': 'int | str', 'default': '300', 'description': 'Metadata popup height in pixels or CSS units. Defaults to 300.'}}, 'postprocess': {'value': {'type': 'numpy.ndarray | PIL.Image.Image | str | pathlib.Path | None', 'description': 'Input image as a NumPy array, PIL Image, string (file path or URL), Path object, or None.'}}, 'preprocess': {'return': {'type': 'numpy.ndarray | PIL.Image.Image | str | ImageMetaData | None', 'description': 'Preprocessed image as a NumPy array, PIL Image, filepath, ImageMetaData, or None.'}, 'value': None}}, 'events': {'clear': {'type': None, 'default': None, 'description': 'This listener is triggered when the user clears the ImageMeta using the clear button for the component.'}, 'change': {'type': None, 'default': None, 'description': 'Triggered when the value of the ImageMeta changes either because of user input (e.g. a user types in a textbox) OR because of a function update (e.g. an image receives a value from the output of an event trigger). See `.input()` for a listener that is only triggered by user input.'}, 'select': {'type': None, 'default': None, 'description': 'Event listener for when the user selects or deselects the ImageMeta. Uses event data gradio.SelectData to carry `value` referring to the label of the ImageMeta, and `selected` to refer to state of the ImageMeta. See EventData documentation on how to use this event data'}, 'upload': {'type': None, 'default': None, 'description': 'This listener is triggered when the user uploads a file into the ImageMeta.'}, 'input': {'type': None, 'default': None, 'description': 'This listener is triggered when the user changes the value of the ImageMeta.'}, 'load_metadata': {'type': None, 'default': None, 'description': "Triggered when the user clicks the 'Load Metadata' button, expecting ImageMetaData as input."}}}, '__meta__': {'additional_interfaces': {'ImageMetaData': {'source': 'class ImageMetaData(ImageData):\n    pass'}}, 'user_fn_refs': {'ImageMeta': ['ImageMetaData']}}}

abs_path = os.path.join(os.path.dirname(__file__), "css.css")

with gr.Blocks(
    css=abs_path,
    theme=gr.themes.Default(
        font_mono=[
            gr.themes.GoogleFont("Inconsolata"),
            "monospace",
        ],
    ),
) as demo:
    gr.Markdown(
"""
# `gradio_imagemeta`

<div style="display: flex; gap: 7px;">
<a href="https://pypi.org/project/gradio_imagemeta/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_imagemeta"></a>  
</div>

Image Preview with Metadata for Gradio Interface
""", elem_classes=["md-custom"], header_links=True)
    app.render()
    gr.Markdown(
"""
## Installation

```bash
pip install gradio_imagemeta
```

## Usage

```python
import gradio as gr
from typing import List, Any, Literal
from gradio_imagemeta import ImageMeta
from gradio_imagemeta.helpers import add_metadata, transfer_metadata
from gradio_propertysheet import PropertySheet
from gradio_propertysheet.helpers import  flatten_dataclass_with_labels
from pathlib import Path
from ui_config import PropertyConfig

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

def load_default_image():
    return "src/examples/image_with_meta.png"

def handle_load_metadata(image_data: gr.EventData) -> List[Any]:
    \"\"\"
    Processes image metadata by calling the agnostic `transfer_metadata` helper.
    \"\"\"
    if not image_data or not hasattr(image_data, "_data"):
        return [gr.skip()] * len(output_fields)

    metadata = image_data._data
    
    if not metadata:
        return [gr.skip()] * len(output_fields)
        
    # --- UI-Specific Configuration ---
    # Define the map that tells the helper how to process the PropertySheet.
    sheet_map = {
        id(property_sheet): {
            "type": property_sheet._dataclass_type, 
            "prefixes": [] # No prefixes needed for this simple case
        }
        
    }
    gradio_map = {
            id(component): label 
            for label, component in input_fields.items()
        }
    # Call the agnostic helper function to do the heavy lifting.
    return transfer_metadata(
        output_fields=output_fields,
        metadata=metadata,
        propertysheet_map=sheet_map,
        gradio_component_map=gradio_map,
        remove_prefix_from_keys=False
    )

def save_image_with_metadata(
    image_data: Any,
    format: Literal[".png", ".png"],
    sheet_state: PropertyConfig,
    model: str, 
    f_number: str, 
    iso: str, 
    s_churn_val: float, 
    description: str
) -> str | None:
    \"\"\"
    Saves an image with updated metadata, merging data from the PropertySheet
    and individual UI components.
    This example deals with the PropertySheet component and the individual gradio components. 
    Since they have the same labels here, we'll simply replace the metadata with each other's values.
    \"\"\"
    if not image_data:
        return None
   
   
    metadata = flatten_dataclass_with_labels(sheet_state)
    individual_component_values = {
        "Model": model,
        "FNumber": f_number,
        "ISOSpeedRatings": iso,
        "Schurn": s_churn_val,
        "Description": description
    }
   
    metadata["Image Settings - Model"] = individual_component_values["Model"]
    metadata["Image Settings - FNumber"] = individual_component_values["FNumber"]
    metadata["Image Settings - ISOSpeedRatings"] = individual_component_values["ISOSpeedRatings"]
    metadata["Image Settings - Schurn"] = individual_component_values["Schurn"]
    metadata["Description"] = individual_component_values["Description"]
   
    final_metadata = {str(key): value for key, value in metadata.items()}
    
    new_filepath = output_dir / f"image_with_meta{format}"
    add_metadata(image_data, new_filepath, final_metadata)
    
    return str(new_filepath)

initial_property_from_meta_config = PropertyConfig()

with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("# ImageMeta Component Demo")    
    gr.Markdown(\"\"\"
        2. Upload demo image or an image with EXIF or PNG metadata using either the "Upload Imagem (Custom metadata only)" component or the "Upload Imagem (all metadata)" component.
        3. Click the 'Info' icon (ⓘ) in the top-left of the image component to view the metadata panel.
        4. Click 'Load Metadata' in the popup to populate the fields below with metadata values (`Model`, `FNumber`, `ISOSpeedRatings`, `Schurn`, `Description`).
        5. The section below displays how metadata is rendered in components and the `PropertySheet` custom component, showing the hierarchical structure of the image settings.
        6. In the "Metadata Viewer" section, you can add field values as metadata to a previously uploaded image in "Upload Image (Custom metadata only)." Then click 'Add metadata and save image' to save a new image with the metadata.
        \"\"\"
    )
    
    property_sheet_state = gr.State(value=initial_property_from_meta_config)
    with gr.Row():
        img_custom = ImageMeta(
            label="Upload Image (Custom metadata only)",
            type="filepath",
            width=600,
            height=400,            
            popup_metadata_height=350,
            popup_metadata_width=550,
            interactive=True,
            only_custom_metadata=True
            
                       
        )
        img_all = ImageMeta(
            label="Upload Image (All metadata)",
            only_custom_metadata=False,
            type="filepath",
            width=600,
            height=400,            
            popup_metadata_height=350,
            popup_metadata_width=550,
            interactive=True
        )

    gr.Markdown("## Metadata Viewer")
    gr.Markdown("### Individual Components")
    with gr.Row():
        model_box = gr.Textbox(label="Model")
        fnumber_box = gr.Textbox(label="FNumber")
        iso_box = gr.Textbox(label="ISOSpeedRatings")
        s_churn = gr.Slider(label="Schurn", value=1.0, minimum=0.0, maximum=1.0, step=0.1)
        description_box = gr.Textbox(label="Description", lines=2)
    
    gr.Markdown("### PropertySheet Component")
    with gr.Row():
        property_sheet = PropertySheet(
            value=initial_property_from_meta_config,
            label="Image Settings",
            width=400,
            height=550,
            visible=True,
            root_label="General"
        )    
    gr.Markdown("## Metadata Editor")
    with gr.Row():
        save_format = gr.Radio(label="Image Format", choices=[".png", ".jpg"], value=".png")
        save_button = gr.Button("Add Metadata and Save Image")
        saved_file_output = gr.File(label="Download Image")
   
        
    input_fields = {
        "Model": model_box,
        "FNumber": fnumber_box,
        "ISOSpeedRatings": iso_box,
        "Schurn": s_churn,
        "Description": description_box
    }
    
    output_fields = [
        property_sheet,
        model_box,
        fnumber_box,
        iso_box,
        s_churn,
        description_box
    ]
    
    img_custom.load_metadata(handle_load_metadata, inputs=None, outputs=output_fields)
    img_all.load_metadata(handle_load_metadata, inputs=None, outputs=output_fields)
    
    def handle_render_change(updated_config: PropertyConfig, current_state: PropertyConfig):
        \"\"\"
        Updates the PropertySheet state when its configuration changes.

        Args:
            updated_config: The new PropertyConfig instance from the PropertySheet.
            current_state: The current PropertyConfig state.

        Returns:
            A tuple of (updated_config, updated_config) or (current_state, current_state) if updated_config is None.
        \"\"\"
        if updated_config is None:
            return current_state, current_state
        return updated_config, updated_config
    
    property_sheet.change(
        fn=handle_render_change,
        inputs=[property_sheet, property_sheet_state],
        outputs=[property_sheet, property_sheet_state]
    )
    save_button.click(
        save_image_with_metadata,
        inputs=[img_custom, save_format, property_sheet, *input_fields.values()],
        outputs=[saved_file_output]
    )
    demo.load(
        fn=load_default_image,
        inputs=None,
        outputs=img_custom
    )
if __name__ == "__main__":
    demo.launch()
```
""", elem_classes=["md-custom"], header_links=True)


    gr.Markdown("""
## `ImageMeta`

### Initialization
""", elem_classes=["md-custom"], header_links=True)

    gr.ParamViewer(value=_docs["ImageMeta"]["members"]["__init__"], linkify=['ImageMetaData'])


    gr.Markdown("### Events")
    gr.ParamViewer(value=_docs["ImageMeta"]["events"], linkify=['Event'])




    gr.Markdown("""

### User function

The impact on the users predict function varies depending on whether the component is used as an input or output for an event (or both).

- When used as an Input, the component only impacts the input signature of the user function.
- When used as an output, the component only impacts the return signature of the user function.

The code snippet below is accurate in cases where the component is used as both an input and an output.

- **As input:** Is passed, preprocessed image as a NumPy array, PIL Image, filepath, ImageMetaData, or None.
- **As output:** Should return, input image as a NumPy array, PIL Image, string (file path or URL), Path object, or None.

 ```python
def predict(
    value: numpy.ndarray | PIL.Image.Image | str | ImageMetaData | None
) -> numpy.ndarray | PIL.Image.Image | str | pathlib.Path | None:
    return value
```
""", elem_classes=["md-custom", "ImageMeta-user-fn"], header_links=True)




    code_ImageMetaData = gr.Markdown("""
## `ImageMetaData`
```python
class ImageMetaData(ImageData):
    pass
```""", elem_classes=["md-custom", "ImageMetaData"], header_links=True)

    demo.load(None, js=r"""function() {
    const refs = {
            ImageMetaData: [], };
    const user_fn_refs = {
          ImageMeta: ['ImageMetaData'], };
    requestAnimationFrame(() => {

        Object.entries(user_fn_refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}-user-fn`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })

        Object.entries(refs).forEach(([key, refs]) => {
            if (refs.length > 0) {
                const el = document.querySelector(`.${key}`);
                if (!el) return;
                refs.forEach(ref => {
                    el.innerHTML = el.innerHTML.replace(
                        new RegExp("\\b"+ref+"\\b", "g"),
                        `<a href="#h-${ref.toLowerCase()}">${ref}</a>`
                    );
                })
            }
        })
    })
}

""")

demo.launch()
