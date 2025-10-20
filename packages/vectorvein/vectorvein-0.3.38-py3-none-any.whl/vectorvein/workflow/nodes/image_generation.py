from ..graph.node import Node
from ..graph.port import PortType, InputPort, OutputPort


class BackgroundGeneration(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="BackgroundGeneration",
            category="image_generation",
            task_name="image_generation.background_generation",
            node_id=id,
            ports={
                "base_image_url": InputPort(
                    name="base_image_url",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                    show=True,
                ),
                "remove_background": InputPort(
                    name="remove_background",
                    port_type=PortType.CHECKBOX,
                    value=True,
                ),
                "remove_background_method": InputPort(
                    name="remove_background_method",
                    port_type=PortType.SELECT,
                    value="accurate",
                    options=[
                        {"value": "fast", "label": "fast"},
                        {"value": "accurate", "label": "accurate"},
                        {"value": "portrait", "label": "portrait"},
                    ],
                    condition="return fieldsData.remove_background.value",
                    condition_python=lambda ports: ports["remove_background"].value,
                ),
                "ref_image_url": InputPort(
                    name="ref_image_url",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                ),
                "ref_prompt": InputPort(
                    name="ref_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    max_length=200,
                    multiple=True,
                ),
                "image_title": InputPort(
                    name="title",
                    port_type=PortType.INPUT,
                    value="",
                    multiple=True,
                ),
                "image_sub_title": InputPort(
                    name="sub_title",
                    port_type=PortType.INPUT,
                    value="",
                    multiple=True,
                ),
                "n": InputPort(
                    name="n",
                    port_type=PortType.NUMBER,
                    value=1,
                ),
                "noise_level": InputPort(
                    name="noise_level",
                    port_type=PortType.NUMBER,
                    value=300,
                ),
                "ref_prompt_weight": InputPort(
                    name="ref_prompt_weight",
                    port_type=PortType.NUMBER,
                    value=0.5,
                ),
                "scene_type": InputPort(
                    name="scene_type",
                    port_type=PortType.SELECT,
                    value="GENERAL",
                    options=[
                        {"value": "GENERAL", "label": "GENERAL"},
                        {"value": "ROOM", "label": "ROOM"},
                        {"value": "COSMETIC", "label": "COSMETIC"},
                    ],
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class DallE(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="DallE",
            category="image_generation",
            task_name="image_generation.dall_e",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "model": InputPort(
                    name="model",
                    port_type=PortType.SELECT,
                    value="dall-e-3",
                    options=[
                        {"value": "dall-e-3", "label": "DALL·E 3"},
                    ],
                ),
                "size": InputPort(
                    name="size",
                    port_type=PortType.SELECT,
                    value="1024x1024",
                    options=[
                        {"value": "1024x1024", "label": "1024x1024"},
                        {"value": "1792x1024", "label": "1792x1024"},
                        {"value": "1024x1792", "label": "1024x1792"},
                    ],
                ),
                "quality": InputPort(
                    name="quality",
                    port_type=PortType.SELECT,
                    value="standard",
                    options=[
                        {"value": "standard", "label": "standard"},
                        {"value": "hd", "label": "hd"},
                    ],
                ),
                "style": InputPort(
                    name="style",
                    port_type=PortType.SELECT,
                    value="vivid",
                    options=[
                        {"value": "vivid", "label": "vivid"},
                        {"value": "natural", "label": "natural"},
                    ],
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Flux1(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Flux1",
            category="image_generation",
            task_name="image_generation.flux1",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "input_image": InputPort(
                    name="input_image",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                    show=True,
                    condition="return fieldsData.model.value.startsWith('FLUX.1 Kontext')",
                    condition_python=lambda ports: ports["model"].value.startswith("FLUX.1 Kontext"),
                ),
                "model": InputPort(
                    name="model",
                    port_type=PortType.SELECT,
                    value="FLUX.1 [dev]",
                    options=[
                        {"value": "FLUX.1 [schnell]", "label": "FLUX.1 [schnell]"},
                        {"value": "FLUX.1 [dev]", "label": "FLUX.1 [dev]"},
                        {"value": "FLUX.1 [pro]", "label": "FLUX.1 [pro]"},
                        {"value": "FLUX.1 [pro] ultra", "label": "FLUX.1 [pro] ultra"},
                        {"value": "FLUX.1 Kontext [pro]", "label": "FLUX.1 Kontext [pro]"},
                        {"value": "FLUX.1 Kontext [max]", "label": "FLUX.1 Kontext [max]"},
                        {"value": "FLUX.1 Kontext [max] Multi", "label": "FLUX.1 Kontext [max] Multi"},
                    ],
                    multiple=True,
                ),
                "width": InputPort(
                    name="width",
                    port_type=PortType.NUMBER,
                    value=1024,
                    max=1536,
                    condition="return fieldsData.model.value !== 'FLUX.1 [pro] ultra' && !fieldsData.model.value.startsWith('FLUX.1 Kontext')",
                    condition_python=lambda ports: ports["model"].value != "FLUX.1 [pro] ultra" and not ports["model"].value.startswith("FLUX.1 Kontext"),
                ),
                "height": InputPort(
                    name="height",
                    port_type=PortType.NUMBER,
                    value=1024,
                    max=1536,
                    condition="return fieldsData.model.value !== 'FLUX.1 [pro] ultra' && !fieldsData.model.value.startsWith('FLUX.1 Kontext')",
                    condition_python=lambda ports: ports["model"].value != "FLUX.1 [pro] ultra" and not ports["model"].value.startswith("FLUX.1 Kontext"),
                ),
                "aspect_ratio": InputPort(
                    name="aspect_ratio",
                    port_type=PortType.SELECT,
                    value="16:9",
                    options=[
                        {"value": "21:9", "label": "21:9"},
                        {"value": "16:9", "label": "16:9"},
                        {"value": "4:3", "label": "4:3"},
                        {"value": "1:1", "label": "1:1"},
                        {"value": "3:4", "label": "3:4"},
                        {"value": "9:16", "label": "9:16"},
                        {"value": "9:21", "label": "9:21"},
                    ],
                    condition="return fieldsData.model.value === 'FLUX.1 [pro] ultra'",
                    condition_python=lambda ports: ports["model"].value == "FLUX.1 [pro] ultra",
                ),
                "raw": InputPort(
                    name="raw",
                    port_type=PortType.CHECKBOX,
                    value=False,
                    condition="return fieldsData.model.value === 'FLUX.1 [pro] ultra'",
                    condition_python=lambda ports: ports["model"].value == "FLUX.1 [pro] ultra",
                ),
                "steps": InputPort(
                    name="steps",
                    port_type=PortType.NUMBER,
                    value=30,
                ),
                "cfg_scale": InputPort(
                    name="cfg_scale",
                    port_type=PortType.NUMBER,
                    value=7,
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Inpainting(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Inpainting",
            category="image_generation",
            task_name="image_generation.inpainting",
            node_id=id,
            ports={
                "input_image": InputPort(
                    name="input_image",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                    show=True,
                ),
                "inpainting_method": InputPort(
                    name="inpainting_method",
                    port_type=PortType.SELECT,
                    value="smart",
                    options=[
                        {"value": "smart", "label": "smart"},
                        {"value": "custom", "label": "custom"},
                    ],
                ),
                "mask_image": InputPort(
                    name="mask_image",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    condition="return fieldsData.inpainting_method.value === 'custom'",
                    condition_python=lambda ports: ports["inpainting_method"].value == "custom",
                    multiple=True,
                ),
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                ),
                "model": InputPort(
                    name="model",
                    port_type=PortType.SELECT,
                    value="FLUX.1 [pro] Fill",
                    options=[
                        {"value": "FLUX.1 [pro] Fill", "label": "FLUX.1 [pro] Fill"},
                        {"value": "FLUX.1 [dev] Fill", "label": "FLUX.1 [dev] Fill"},
                        {"value": "Stable Diffusion XL", "label": "Stable Diffusion XL"},
                    ],
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
                "output_mask": OutputPort(
                    condition="return fieldsData.inpainting_method.value === 'smart'",
                    condition_python=lambda ports: ports["inpainting_method"].value == "smart",
                ),
            },
        )


class Kolors(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Kolors",
            category="image_generation",
            task_name="image_generation.kolors",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "negative_prompt": InputPort(
                    name="negative_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "width": InputPort(
                    name="width",
                    port_type=PortType.NUMBER,
                    value=1024,
                ),
                "height": InputPort(
                    name="height",
                    port_type=PortType.NUMBER,
                    value=1024,
                ),
                "steps": InputPort(
                    name="steps",
                    port_type=PortType.NUMBER,
                    value=30,
                ),
                "cfg_scale": InputPort(
                    name="cfg_scale",
                    port_type=PortType.NUMBER,
                    value=7,
                ),
                "scheduler": InputPort(
                    name="scheduler",
                    port_type=PortType.SELECT,
                    value="EulerDiscreteScheduler",
                    options=[
                        {"value": "EulerDiscreteScheduler", "label": "EulerDiscreteScheduler"},
                        {"value": "EulerAncestralDiscreteScheduler", "label": "EulerAncestralDiscreteScheduler"},
                        {"value": "DPMSolverMultistepScheduler", "label": "DPMSolverMultistepScheduler"},
                        {"value": "DPMSolverMultistepScheduler_SDE_karras", "label": "DPMSolverMultistepScheduler_SDE_karras"},
                        {"value": "UniPCMultistepScheduler", "label": "UniPCMultistepScheduler"},
                        {"value": "DEISMultistepScheduler", "label": "DEISMultistepScheduler"},
                    ],
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Pulid(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Pulid",
            category="image_generation",
            task_name="image_generation.pulid",
            node_id=id,
            ports={
                "reference_image": InputPort(
                    name="reference_image",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                    show=True,
                ),
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                    show=True,
                ),
                "negative_prompt": InputPort(
                    name="negative_prompt",
                    port_type=PortType.TEXTAREA,
                    value="bad quality, worst quality, text, signature, watermark, extra limbs",
                ),
                "image_size": InputPort(
                    name="image_size",
                    port_type=PortType.SELECT,
                    value="landscape_4_3",
                    options=[
                        {"value": "square_hd", "label": "square_hd"},
                        {"value": "square", "label": "square"},
                        {"value": "portrait_4_3", "label": "portrait_4_3"},
                        {"value": "portrait_16_9", "label": "portrait_16_9"},
                        {"value": "landscape_4_3", "label": "landscape_4_3"},
                        {"value": "landscape_16_9", "label": "landscape_16_9"},
                        {"value": "custom", "label": "custom"},
                    ],
                ),
                "custom_width": InputPort(
                    name="custom_width",
                    port_type=PortType.NUMBER,
                    value=1024,
                    condition="return fieldsData.image_size.value === 'custom'",
                    condition_python=lambda ports: ports["image_size"].value == "custom",
                ),
                "custom_height": InputPort(
                    name="custom_height",
                    port_type=PortType.NUMBER,
                    value=768,
                    condition="return fieldsData.image_size.value === 'custom'",
                    condition_python=lambda ports: ports["image_size"].value == "custom",
                ),
                "num_inference_steps": InputPort(
                    name="num_inference_steps",
                    port_type=PortType.NUMBER,
                    value=20,
                ),
                "seed": InputPort(
                    name="seed",
                    port_type=PortType.NUMBER,
                    value=-1,
                ),
                "guidance_scale": InputPort(
                    name="guidance_scale",
                    port_type=PortType.NUMBER,
                    value=4,
                ),
                "true_cfg": InputPort(
                    name="true_cfg",
                    port_type=PortType.NUMBER,
                    value=1,
                ),
                "id_weight": InputPort(
                    name="id_weight",
                    port_type=PortType.NUMBER,
                    value=1,
                ),
                "max_sequence_length": InputPort(
                    name="max_sequence_length",
                    port_type=PortType.SELECT,
                    value="256",
                    options=[
                        {"value": "128", "label": "128"},
                        {"value": "256", "label": "256"},
                        {"value": "512", "label": "512"},
                    ],
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class Recraft(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="Recraft",
            category="image_generation",
            task_name="image_generation.recraft",
            node_id=id,
            ports={
                "generation_type": InputPort(
                    name="generation_type",
                    port_type=PortType.SELECT,
                    value="text_to_image",
                    options=[
                        {"value": "text_to_image", "label": "text_to_image"},
                        {"value": "image_to_vector", "label": "image_to_vector"},
                    ],
                ),
                "image_url": InputPort(
                    name="image_url",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=True,
                    condition="return fieldsData.generation_type.value === 'image_to_vector'",
                    condition_python=lambda ports: ports["generation_type"].value == "image_to_vector",
                ),
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    condition="return fieldsData.generation_type.value === 'text_to_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image",
                    multiple=True,
                ),
                "base_style": InputPort(
                    name="base_style",
                    port_type=PortType.SELECT,
                    value="any",
                    options=[
                        {"value": "any", "label": "any"},
                        {"value": "realistic_image", "label": "realistic_image"},
                        {"value": "digital_illustration", "label": "digital_illustration"},
                        {"value": "vector_illustration", "label": "vector_illustration"},
                    ],
                    condition="return fieldsData.generation_type.value === 'text_to_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image",
                    multiple=True,
                ),
                "substyle_realistic_image": InputPort(
                    name="substyle_realistic_image",
                    port_type=PortType.SELECT,
                    value="null",
                    options=[
                        {"value": "null", "label": "null"},
                        {"value": "b_and_w", "label": "b_and_w"},
                        {"value": "hard_flash", "label": "hard_flash"},
                        {"value": "hdr", "label": "hdr"},
                        {"value": "natural_light", "label": "natural_light"},
                        {"value": "studio_portrait", "label": "studio_portrait"},
                        {"value": "enterprise", "label": "enterprise"},
                        {"value": "motion_blur", "label": "motion_blur"},
                    ],
                    condition="return fieldsData.generation_type.value === 'text_to_image' && fieldsData.base_style.value === 'realistic_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image" and ports["base_style"].value == "realistic_image",
                    multiple=True,
                ),
                "substyle_digital_illustration": InputPort(
                    name="substyle_digital_illustration",
                    port_type=PortType.SELECT,
                    value="null",
                    options=[
                        {"value": "null", "label": "null"},
                        {"value": "pixel_art", "label": "pixel_art"},
                        {"value": "hand_drawn", "label": "hand_drawn"},
                        {"value": "grain", "label": "grain"},
                        {"value": "infantile_sketch", "label": "infantile_sketch"},
                        {"value": "2d_art_poster", "label": "2d_art_poster"},
                        {"value": "handmade_3d", "label": "handmade_3d"},
                        {"value": "hand_drawn_outline", "label": "hand_drawn_outline"},
                        {"value": "engraving_color", "label": "engraving_color"},
                        {"value": "2d_art_poster_2", "label": "2d_art_poster_2"},
                    ],
                    condition="return fieldsData.generation_type.value === 'text_to_image' && fieldsData.base_style.value === 'digital_illustration'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image" and ports["base_style"].value == "digital_illustration",
                    multiple=True,
                ),
                "substyle_vector_illustration": InputPort(
                    name="substyle_vector_illustration",
                    port_type=PortType.SELECT,
                    value="null",
                    options=[
                        {"value": "null", "label": "null"},
                        {"value": "engraving", "label": "engraving"},
                        {"value": "line_art", "label": "line_art"},
                        {"value": "line_circuit", "label": "line_circuit"},
                        {"value": "linocut", "label": "linocut"},
                    ],
                    condition="return fieldsData.generation_type.value === 'text_to_image' && fieldsData.base_style.value === 'vector_illustration'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image" and ports["base_style"].value == "vector_illustration",
                    multiple=True,
                ),
                "size": InputPort(
                    name="size",
                    port_type=PortType.SELECT,
                    value="1024x1024",
                    options=[
                        {"value": "1024x1024", "label": "1024x1024"},
                        {"value": "1365x1024", "label": "1365x1024"},
                        {"value": "1024x1365", "label": "1024x1365"},
                        {"value": "1536x1024", "label": "1536x1024"},
                        {"value": "1024x1536", "label": "1024x1536"},
                        {"value": "1820x1024", "label": "1820x1024"},
                        {"value": "1024x1820", "label": "1024x1820"},
                        {"value": "1024x2048", "label": "1024x2048"},
                        {"value": "2048x1024", "label": "2048x1024"},
                        {"value": "1434x1024", "label": "1434x1024"},
                        {"value": "1024x1434", "label": "1024x1434"},
                        {"value": "1024x1280", "label": "1024x1280"},
                        {"value": "1280x1024", "label": "1280x1024"},
                        {"value": "1024x1707", "label": "1024x1707"},
                        {"value": "1707x1024", "label": "1707x1024"},
                    ],
                    condition="return fieldsData.generation_type.value === 'text_to_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image",
                ),
                "colors": InputPort(
                    name="colors",
                    port_type=PortType.COLOR,
                    value=[],
                    multiple=True,
                    condition="return fieldsData.generation_type.value === 'text_to_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image",
                ),
                "background_color": InputPort(
                    name="background_color",
                    port_type=PortType.COLOR,
                    value=[],
                    multiple=True,
                    max_count=1,
                    condition="return fieldsData.generation_type.value === 'text_to_image'",
                    condition_python=lambda ports: ports["generation_type"].value == "text_to_image",
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class GptImage(Node):
    def __init__(self, id: str | None = None):
        super().__init__(
            node_type="GptImage",
            category="image_generation",
            task_name="image_generation.gpt_image",
            node_id=id,
            ports={
                "action": InputPort(
                    name="action",
                    port_type=PortType.SELECT,
                    value="generation",
                    options=[
                        {"value": "generation", "label": "generation"},
                        {"value": "edit", "label": "edit"},
                    ],
                ),
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                    show=True,
                ),
                "individual_images": InputPort(
                    name="individual_images",
                    port_type=PortType.CHECKBOX,
                    value=False,
                    condition="return fieldsData.action.value === 'edit'",
                    condition_python=lambda ports: ports["action"].value == "edit",
                ),
                "image": InputPort(
                    name="image",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".jpg", ".jpeg", ".png", ".webp"],
                    multiple=False,
                    condition="return fieldsData.action.value === 'edit'",
                    condition_python=lambda ports: ports["action"].value == "edit",
                ),
                "mask": InputPort(
                    name="mask",
                    port_type=PortType.FILE,
                    value=[],
                    support_file_types=[".png"],
                    condition="return fieldsData.action.value === 'edit'",
                    condition_python=lambda ports: ports["action"].value == "edit",
                ),
                "model": InputPort(
                    name="model",
                    port_type=PortType.SELECT,
                    value="gpt-image-1",
                    options=[
                        {"value": "gpt-image-1", "label": "gpt-image-1"},
                    ],
                    multiple=True,
                ),
                "size": InputPort(
                    name="size",
                    port_type=PortType.SELECT,
                    value="1024x1024",
                    options=[
                        {"value": "1024x1024", "label": "1024x1024"},
                        {"value": "1024x1536", "label": "1024x1536"},
                        {"value": "1536x1024", "label": "1536x1024"},
                    ],
                    multiple=True,
                ),
                "n": InputPort(
                    name="n",
                    port_type=PortType.NUMBER,
                    value=1,
                    min=1,
                    max=10,
                ),
                "quality": InputPort(
                    name="quality",
                    port_type=PortType.SELECT,
                    value="high",
                    options=[
                        {"value": "low", "label": "low"},
                        {"value": "medium", "label": "medium"},
                        {"value": "high", "label": "high"},
                    ],
                    multiple=True,
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )


class StableDiffusion(Node):
    def __init__(self, id: str | None = None):
        special_width_height_models = [
            "stable-diffusion-xl-1024-v0-9",
            "stable-diffusion-xl-1024-v1-0",
        ]
        sd3_models = [
            "sd-ultra",
            "sd3-large",
            "sd3-large-turbo",
            "sd3-medium",
            "sd3.5-large",
            "sd3.5-large-turbo",
            "sd3.5-medium",
            "sd-core",
        ]

        super().__init__(
            node_type="StableDiffusion",
            category="image_generation",
            task_name="image_generation.stable_diffusion",
            node_id=id,
            ports={
                "prompt": InputPort(
                    name="prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "negative_prompt": InputPort(
                    name="negative_prompt",
                    port_type=PortType.TEXTAREA,
                    value="",
                    multiple=True,
                ),
                "model": InputPort(
                    name="model",
                    port_type=PortType.SELECT,
                    value="stable-diffusion-xl-1024-v1-0",
                    options=[
                        {"value": "sd-ultra", "label": "Ultra"},
                        {"value": "sd3.5-large", "label": "Stable Diffusion 3.5 Large"},
                        {"value": "sd3-large", "label": "Stable Diffusion 3 Large"},
                        {"value": "sd3.5-large-turbo", "label": "Stable Diffusion 3.5 Large Turbo"},
                        {"value": "sd3-large-turbo", "label": "Stable Diffusion 3 Large Turbo"},
                        {"value": "sd3.5-medium", "label": "Stable Diffusion 3.5 Medium"},
                        {"value": "sd3-medium", "label": "Stable Diffusion 3 Medium"},
                        {"value": "sd-core", "label": "Core"},
                        {"value": "stable-diffusion-xl-1024-v1-0", "label": "SDXL 1.0"},
                        {"value": "stable-diffusion-xl-1024-v0-9", "label": "SDXL 0.9"},
                    ],
                ),
                "cfg_scale": InputPort(
                    name="cfg_scale",
                    port_type=PortType.NUMBER,
                    value=7,
                    condition=f"return !{sd3_models}.includes(fieldsData.model.value)",
                ),
                "sampler": InputPort(
                    name="sampler",
                    port_type=PortType.SELECT,
                    value="k_dpmpp_2m",
                    options=[
                        {"value": "ddim", "label": "ddim"},
                        {"value": "plms", "label": "plms"},
                        {"value": "k_euler", "label": "k_euler"},
                        {"value": "k_euler_ancestral", "label": "k_euler_ancestral"},
                        {"value": "k_heun", "label": "k_heun"},
                        {"value": "k_dpm_2", "label": "k_dpm_2"},
                        {"value": "k_dpm_2_ancestral", "label": "k_dpm_2_ancestral"},
                        {"value": "k_dpmpp_2s_ancestral", "label": "k_dpmpp_2s_ancestral"},
                        {"value": "k_dpmpp_2m", "label": "k_dpmpp_2m"},
                        {"value": "k_dpmpp_sde", "label": "k_dpmpp_sde"},
                    ],
                    condition=f"return !{sd3_models}.includes(fieldsData.model.value)",
                ),
                "size": InputPort(
                    name="size",
                    port_type=PortType.SELECT,
                    value="1024 x 1024",
                    options=[
                        {"value": "1024 x 1024", "label": "1024 x 1024"},
                        {"value": "1152 x 896", "label": "1152 x 896"},
                        {"value": "896 x 1152", "label": "896 x 1152"},
                        {"value": "1216 x 832", "label": "1216 x 832"},
                        {"value": "832 x 1216", "label": "832 x 1216"},
                        {"value": "1344 x 768", "label": "1344 x 768"},
                        {"value": "768 x 1344", "label": "768 x 1344"},
                        {"value": "1536 x 640", "label": "1536 x 640"},
                        {"value": "640 x 1536", "label": "640 x 1536"},
                    ],
                    condition=f"return {special_width_height_models}.includes(fieldsData.model.value) && !{sd3_models}.includes(fieldsData.model.value)",
                ),
                "aspect_ratio": InputPort(
                    name="aspect_ratio",
                    port_type=PortType.SELECT,
                    value="1:1",
                    options=[
                        {"value": "1:1", "label": "1:1"},
                        {"value": "16:9", "label": "16:9"},
                        {"value": "21:9", "label": "21:9"},
                        {"value": "2:3", "label": "2:3"},
                        {"value": "3:2", "label": "3:2"},
                        {"value": "4:5", "label": "4:5"},
                        {"value": "5:4", "label": "5:4"},
                        {"value": "9:16", "label": "9:16"},
                        {"value": "9:21", "label": "9:21"},
                    ],
                    condition=f"return {sd3_models}.includes(fieldsData.model.value)",
                ),
                "output_type": InputPort(
                    name="output_type",
                    port_type=PortType.SELECT,
                    value="markdown",
                    options=[
                        {"value": "only_link", "label": "only_link"},
                        {"value": "markdown", "label": "markdown"},
                        {"value": "html", "label": "html"},
                    ],
                ),
                "output": OutputPort(),
            },
        )
