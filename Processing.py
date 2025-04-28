import chainlit as cl
import asyncio

@cl.on_message
async def on_message(message: cl.Message):
    response = "This is a streaming message with animated processing dots!"
    final_message = ""

    # Start a processing animation message
    processing = cl.Message(content="Processing")
    await processing.send()

    # Start a streaming message (empty first)
    streaming_msg = cl.Message(content="")
    await streaming_msg.send()

    # Create a task that updates the "Processing..." animation
    async def animate_processing():
        dots = ""
        while True:
            dots += "."
            if len(dots) > 3:
                dots = ""
            await processing.update(content=f"Processing{dots}")
            await asyncio.sleep(0.5)  # Adjust the speed of animation

    animation_task = asyncio.create_task(animate_processing())

    # Stream the response character by character
    for char in response:
        final_message += char
        await asyncio.sleep(0.03)
        await streaming_msg.update(content=final_message)

    # After streaming is done, cancel the animation
    animation_task.cancel()
    try:
        await animation_task
    except asyncio.CancelledError:
        pass

    # Finally remove the processing message
    await processing.remove()
