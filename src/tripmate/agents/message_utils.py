def extract_message_text(
    content,
) -> str:

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for block in content:

            if isinstance(block, dict):

                text = block.get(
                    "text"
                )

                if text:
                    text_parts.append(
                        text
                    )

            else:
                text_parts.append(
                    str(block)
                )

        return "\n".join(
            text_parts
        )

    return str(content)