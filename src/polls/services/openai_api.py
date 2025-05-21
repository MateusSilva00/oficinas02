from time import perf_counter

from openai import OpenAI

from logger import logger

client = OpenAI(api_key='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')

def generate_image_description(base64_top_view, base64_front_view):
    logger.debug("Starting image description generation.")
    start_time = perf_counter()

    response = client.responses.create(
    model="gpt-4.1-mini",
    input=[
        {
            "role": "user",
            "content": [
                { 
                  "type": "input_text",  
                  "text": (
                        "Observe cuidadosamente os produtos nas duas imagens seguintes "
                        "e responda APENAS com os itens visualizados e suas quantidades, "
                        "seguindo o formato:\n"
                        "- X produto\n"
                        "- Y produto\n"
                        "Não inclua nenhum outro comentário ou explicação. Tenha em mente que as imagens são as mesmas\n"
                        "mas vistas de ângulos diferentes. "
                        "A imagem 1 é a visão de cima e a imagem 2 é a visão frontal. "
                        "As imagens sempre conterão os mesmos produtos, portanto não duplique sua quantidade na respostas"
                    ) 
                 },
                {
                  "type": "input_image",
                  "image_url": f"data:image/jpeg;base64,{base64_top_view}",
                  "detail":  "low"
                },
                {
                  "type": "input_image",
                  "image_url": f"data:image/jpeg;base64,{base64_front_view}",
                  "detail": "low"
                },
            ],
        }
        ],
        temperature=0.2,
    )

    end_time = perf_counter()
    elapsed_time = end_time - start_time
    logger.debug(f"Image description generation completed in {elapsed_time:.2f} seconds.")

    return response.model_dump()