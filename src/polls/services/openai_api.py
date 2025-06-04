from time import perf_counter

from openai import OpenAI

from logger import logger

client = OpenAI(
    api_key="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"
)


def generate_image_description(base64_top_view, input_text, base64_front_view=None):
    logger.debug("Starting image description generation.")
    start_time = perf_counter()

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": input_text},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_top_view}",
                        "detail": "low",
                    },
                    # {
                    #   "type": "input_image",
                    #   "image_url": f"data:image/jpeg;base64,{base64_front_view}",
                    #   "detail": "low"
                    # },
                ],
            }
        ],
        temperature=0.2,
    )

    end_time = perf_counter()
    elapsed_time = end_time - start_time
    logger.debug(
        f"Image description generation completed in {elapsed_time:.2f} seconds."
    )

    return response.model_dump()
