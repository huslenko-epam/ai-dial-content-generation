import asyncio
from io import BytesIO
from pathlib import Path

from task._models.custom_content import Attachment, CustomContent
from task._utils.constants import API_KEY, DIAL_URL, DIAL_CHAT_COMPLETIONS_ENDPOINT
from task._utils.bucket_client import DialBucketClient
from task._utils.model_client import DialModelClient
from task._models.message import Message
from task._models.role import Role


async def _put_image() -> Attachment:
    file_name = "dialx-banner.png"
    image_path = Path(__file__).parent.parent.parent / file_name
    mime_type_png = "image/png"

    # TODO:
    #  1. Create DialBucketClient
    #  2. Open image file
    #  3. Use BytesIO to load bytes of image
    #  4. Upload file with client
    #  5. Return Attachment object with title (file name), url and type (mime type)

    async with DialBucketClient(API_KEY, DIAL_URL) as dial_bucket_client:
        with open(image_path, "rb") as img_file:
            img_bytes = img_file.read()

        img_buffer = BytesIO(img_bytes)

        uploaded_file_response = await dial_bucket_client.put_file(
            file_name, mime_type_png, img_buffer
        )

    return Attachment(
        title=file_name, url=uploaded_file_response["url"], type=mime_type_png
    )


def start() -> None:
    # TODO:
    #  1. Create DialModelClient
    #  2. Upload image (use `_put_image` method )
    #  3. Print attachment to see result
    #  4. Call chat completion via client with list containing one Message:
    #    - role: Role.USER
    #    - content: "What do you see on this picture?"
    #    - custom_content: CustomContent(attachments=[attachment])
    #  ---------------------------------------------------------------------------------------------------------------
    #  Note: This approach uploads the image to DIAL bucket and references it via attachment. The key benefit of this
    #        approach that we can use Models from different vendors (OpenAI, Google, Anthropic). The DIAL Core
    #        adapts this attachment to Message content in appropriate format for Model.
    #  TRY THIS APPROACH WITH DIFFERENT MODELS!
    #  Optional: Try upload 2+ pictures for analysis

    dial_model_client = DialModelClient(
        DIAL_CHAT_COMPLETIONS_ENDPOINT, "gpt-4o", API_KEY
    )

    attachment = asyncio.run(_put_image())

    print(f"Attachment: {attachment}")

    message = Message(
        role=Role.USER,
        content="What do you see on this picture?",
        custom_content=CustomContent(attachments=[attachment]),
    )

    response_message = dial_model_client.get_completion([message])

    print(f"Agent: {response_message.content}")


start()
