import torch
from torch import nn

def export_for_libtorch(output_dir, model):

    if not isinstance(model, nn.Module):
        raise TypeError(f"Expected a torch.nn.Module, but got {type(model).__name__}")

    classname = model.__class__.__name__
    filename = f"{classname}_torchscript.pt"
    path = f"{output_dir}/{filename}"

    model.eval()
    scripted = torch.jit.script(model)
    scripted.save(path)