import functools
import torch
import numpy as np
import gradio as gr
import os

from contextlib import contextmanager
from typing import TYPE_CHECKING, Union

from tts_webui.utils.manage_model_state import (
    manage_model_state,
    rename_model,
    get_current_model,
)
from tts_webui.utils.split_text_functions import split_and_recombine_text
from tts_webui.utils.get_path_from_root import get_path_from_root

from .InterruptionFlag import interruptible, InterruptionFlag


if TYPE_CHECKING:
    from chatterbox.tts import ChatterboxTTS
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS


def get_best_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def resolve_device(device):
    return get_best_device() if device == "auto" else device


def resolve_dtype(dtype):
    return {
        "float32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
    }[dtype]


def t3_to(model: "ChatterboxTTS", dtype):
    model.t3.to(dtype=dtype)
    model.conds.t3.to(dtype=dtype)
    return model


def s3gen_to(model: "ChatterboxTTS", dtype):
    if dtype == torch.float16:
        model.s3gen.flow.fp16 = True
    elif dtype == torch.float32:
        model.s3gen.flow.fp16 = False
    else:
        raise NotImplementedError(f"Unsupported dtype {dtype}")
    # model.s3gen.flow.to(dtype=dtype)
    model.s3gen.to(dtype=dtype)
    model.s3gen.mel2wav.to(dtype=torch.float32)
    # due to "Error: cuFFT doesn't support tensor of type: BFloat16" from torch.stft
    # and other errors and general instability
    model.s3gen.tokenizer.to(dtype=torch.float32)
    model.s3gen.speaker_encoder.to(dtype=torch.float32)
    return model


def chatterbox_tts_to(model: "ChatterboxTTS", device, dtype):
    print(f"Moving model to {str(device)}, {str(dtype)}")

    model.ve.to(device=device)
    # model.conds.to(device=device)
    # model.t3.to(device=device, dtype=dtype)
    t3_to(model, dtype)
    # model.s3gen.to(device=device, dtype=dtype)
    # # due to "Error: cuFFT doesn't support tensor of type: BFloat16" from torch.stft
    # model.s3gen.tokenizer.to(dtype=torch.float32)
    s3gen_to(model, dtype if dtype != torch.bfloat16 else torch.float16)
    model.device = device
    torch.cuda.empty_cache()

    return model


@manage_model_state("chatterbox")
def get_model(
    model_name="just_a_placeholder", device=torch.device("cuda"), dtype=torch.float32
) -> Union["ChatterboxTTS", "ChatterboxMultilingualTTS"]:
    if model_name == "multilingual":
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS

        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    else:
        from chatterbox.tts import ChatterboxTTS

        model = ChatterboxTTS.from_pretrained(device=device)
    # having everything on float32 increases performance
    return chatterbox_tts_to(model, device, dtype)


@manage_model_state("chatterbox-vc")
def get_model_vc(
    model_name="just_a_placeholder", device=torch.device("cuda"), dtype=torch.float32
):
    from chatterbox.vc import ChatterboxVC

    return ChatterboxVC.from_pretrained(device=device)


def move_model_to_device_and_dtype(device, dtype, cpu_offload):
    model = get_current_model("chatterbox")
    device = resolve_device(device)
    dtype = resolve_dtype(dtype)
    if model is None:
        get_model("just_a_placeholder", device, dtype)
        return True
    rename_model("chatterbox", generate_model_name(device, dtype))
    device = torch.device("cpu" if cpu_offload else device)
    model = chatterbox_tts_to(model, device, dtype)
    return True


def generate_model_name(device, dtype):
    return f"Chatterbox on {device} with {dtype}"


@contextmanager
def chatterbox_model(model_name, device="cuda", dtype=torch.float32):
    model = get_model(
        model_name=model_name,
        device=torch.device(device),
        dtype=dtype,
    )

    with torch.no_grad():
        yield model


@contextmanager
def cpu_offload_context(model, device, dtype, cpu_offload=False):
    if cpu_offload:
        chatterbox_tts_to(model, torch.device(device), dtype)
    yield model
    if cpu_offload:
        chatterbox_tts_to(model, torch.device("cpu"), dtype)


@interruptible
def _tts_generator(
    text,
    exaggeration=0.5,
    cfg_weight=0.5,
    temperature=0.8,
    audio_prompt_path=None,
    # model
    model_name="just_a_placeholder",
    language_id="en",
    device="cuda",
    dtype="float32",
    cpu_offload=False,
    # hyperparameters
    chunked=False,
    cache_voice=False,
    # chunks
    desired_length=200,
    max_length=300,
    halve_first_chunk=False,
    seed=-1,  # for signature compatibility
    progress=gr.Progress(),
    streaming=False,
    max_new_tokens=1000,
    max_cache_len=1500,  # Affects the T3 speed, hence important
    initial_forward_pass_backend="eager",
    generate_token_backend="cudagraphs-manual",
    **kwargs,
):
    device = resolve_device(device)
    dtype = resolve_dtype(dtype)

    print(f"Using device: {device}")

    progress(0.0, desc="Retrieving model...")
    with chatterbox_model(
        model_name=model_name,
        device=device,
        dtype=dtype,
    ) as model, cpu_offload_context(model, device, dtype, cpu_offload):
        progress(0.1, desc="Generating audio...")

        # save time on subsequent calls
        if audio_prompt_path is not None:
            model.prepare_conditionals(audio_prompt_path, exaggeration=exaggeration)
            if dtype != torch.float32:
                model.conds.t3.to(dtype=dtype)

        def generate_chunk(text):
            print(f"Generating chunk: {text}")
            yield from model.generate(
                text,
                # audio_prompt_path=audio_prompt_path,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                temperature=temperature,
                language_id=language_id,
                # Not implemented
                # cache_voice=cache_voice,
                max_new_tokens=max_new_tokens,
                max_cache_len=max_cache_len,
                t3_params={
                    "initial_forward_pass_backend": initial_forward_pass_backend,
                    "generate_token_backend": generate_token_backend,
                },
            )

        texts = (
            split_and_recombine_text(text, desired_length, max_length)
            if chunked
            else [text]
        )
        if halve_first_chunk:
            texts = (
                split_and_recombine_text(texts[0], desired_length // 2, max_length // 2)
                + texts[1:]
            )
        for i, chunk in enumerate(texts):
            if not streaming:
                progress(i / len(texts), desc=f"Generating chunk: {chunk}")
            for wav in generate_chunk(chunk):
                yield {
                    "audio_out": (model.sr, wav.squeeze().cpu().numpy()),
                }


global_interrupt_flag = InterruptionFlag()


@functools.wraps(_tts_generator)
def tts_stream(*args, **kwargs):
    try:
        yield from _tts_generator(
            *args, interrupt_flag=global_interrupt_flag, streaming=True, **kwargs
        )
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise gr.Error(f"Error: {e}")


@functools.wraps(_tts_generator)
def tts(*args, **kwargs):
    try:
        wavs = list(
            _tts_generator(*args, interrupt_flag=global_interrupt_flag, **kwargs)
        )
        if not wavs:
            raise gr.Error("No audio generated")
        full_wav = np.concatenate([x["audio_out"][1] for x in wavs], axis=0)
        return {
            "audio_out": (wavs[0]["audio_out"][0], full_wav),
        }
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise gr.Error(f"Error: {e}")


def vc(
    audio_in: str,
    audio_ref: str,
    progress=gr.Progress(),
    **kwargs,
):
    progress(0.0, desc="Retrieving model...")
    device = get_best_device()

    print(f"Using device: {device}")

    model = get_model_vc(model_name="just_a_placeholder", device=device)
    progress(0.1, desc="Converting audio...")
    wav = model.generate(
        audio=audio_in,
        target_voice_path=audio_ref,
    )
    return {
        "audio_out": (model.sr, wav.squeeze().cpu().numpy()),
    }


def get_voices():
    voices_dir = get_path_from_root("voices", "chatterbox")
    os.makedirs(voices_dir, exist_ok=True)
    results = [
        (x, os.path.join(voices_dir, x))
        for x in os.listdir(voices_dir)
        if x.endswith(".wav")
    ]
    return results


async def interrupt():
    from .api import global_interrupt_flag

    global_interrupt_flag.interrupt()
    await global_interrupt_flag.join()
    return "Interrupt next chunk"
