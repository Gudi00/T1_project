import torch
print(torch.cuda.device_count())  # должно быть > 0
print(torch.cuda.is_available())  # должно быть True
import intel_extension_for_pytorch as ipex
print(ipex.__version__)  # Должно вывести версию, e.g., 2.1.10