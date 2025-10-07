import torch
print(torch.cuda.device_count())  # должно быть > 0
print(torch.cuda.is_available())  # должно быть True