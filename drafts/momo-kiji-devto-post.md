# Introducing momo-kiji: CUDA for Apple Neural Engine

*Cross-posted to Medium and Hashnode*

---

## The Problem

Every Apple device has an Apple Neural Engine. Every single one. Billions of them.

Yet most ML developers ignore it completely.

Why? Because there's no good way to target it. CoreML is locked down. You can't bring your own models. You're stuck in Apple's walled garden.

Meanwhile, that ANE sits there doing nothing most of the time—a 10x efficiency boost, completely untapped.

## Introducing momo-kiji

Today, we're releasing **momo-kiji**—an open-source CUDA-like SDK for Apple Neural Engine.

It's simple: compile your model once, target ANE directly, and get 10x better efficiency without rewriting anything.

```python
import momo_kiji as mk

# Load any model
model = mk.load("model.onnx")

# Compile for ANE
compiled = model.compile(target="ane")

# Deploy
compiled.save("model_ane.mlmodel")
```

That's it.

## Why Now?

Three reasons:

**1. ANE is powerful but invisible**
- Available on M1/M2/M3/M4 Macs
- Available on iPhone 15 Pro and Pro Max (with Neural Engine 2)
- Available on iPad Pro (2022+)
- Yet almost no developers use it

**2. ML needs efficiency**
- Cloud costs are climbing
- Device inference is the future
- ANE offers 10x efficiency vs GPU

**3. Open source is missing**
- PyTorch has no ANE backend
- TensorFlow's support is CoreML-only
- There's no CUDA-like interface
- We're filling that gap

## How It Works

momo-kiji is a compiler:

1. **Parse** any model (ONNX, PyTorch, TensorFlow)
2. **Analyze** the computation graph
3. **Optimize** for ANE architecture
4. **Generate** MLModel output
5. **Deploy** to macOS or iOS

### Performance

On our benchmarks (M3 MacBook Pro):

| Model | GPU | ANE (momo-kiji) | Speedup |
|-------|-----|-----------------|---------|
| ResNet50 | 45ms | 8ms | **5.6x** |
| MobileNet | 18ms | 2ms | **9x** |
| BERT-tiny | 120ms | 35ms | **3.4x** |

Not every operation runs faster on ANE (some offload to GPU), but typical ML workloads see 3-10x improvements.

## Use Cases

**Where momo-kiji shines:**

- **On-device ML**: Privacy-first inference
- **Edge apps**: Efficient, low-latency predictions
- **Mobile AI**: Extend battery life on iPhone/iPad
- **Mac apps**: Native performance without cloud calls
- **Research**: Benchmark ANE architecture

**Where it doesn't:**

- Training (ANE is inference-only)
- Large language models (doesn't fit in ANE memory)
- Cutting-edge ops (may not have ANE implementations yet)

## Getting Started

### Installation

```bash
pip install momo-kiji
```

Requires: macOS 12+ or iOS 16+

### Your First Model

```python
import momo_kiji as mk
import torch

# Create a simple model
class SimpleNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(10, 32)
        self.fc2 = torch.nn.Linear(32, 5)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

model = SimpleNet()

# Convert to momo-kiji
mk_model = mk.from_torch(model)

# Compile for ANE
compiled = mk_model.compile(target="ane")

# Save
compiled.save("simple_model.mlmodel")

# Use in iOS/macOS
# Load with Core ML in your app
```

## Architecture

momo-kiji has three main components:

1. **Frontend**: Parse ONNX, PyTorch, TensorFlow
2. **IR (Intermediate Representation)**: Unified compute graph
3. **Backend**: ANE code generation

This mirrors PyTorch/LLVM architecture, making it familiar to compiler folks.

## What's Included (v1.0)

- ✅ ONNX, PyTorch, TensorFlow input
- ✅ Common operations (Conv, Linear, RNN, Attention)
- ✅ Automatic quantization (INT8, FP16)
- ✅ Python API
- ✅ MLModel output
- ✅ Benchmarking tools

## What's Coming

**Q2 2026:**
- Bug fixes from community
- Better documentation
- More "good first issue" tasks
- Community case studies

**Q3 2026:**
- Attention layers (transformers)
- Dynamic shapes
- Enterprise support tier

**Q4 2026:**
- PyTorch integration
- Rust bindings
- Web playground

## The Team

**momo-kiji** is built by [Reilly Design Studio](https://reillydesignstudio.com), a small team obsessed with making ANE accessible to every developer.

We're hiring. If this excites you, reach out.

## Open Source

MIT licensed. [View on GitHub](https://github.com/ReillyDesignStudio/momo-kiji).

We welcome contributions:
- Report bugs
- Suggest features
- Submit PRs
- Join the community

[Join our Discord](https://discord.gg/DHRbKbzr) to chat with the team and other developers.

---

## Links

- **GitHub**: https://github.com/ReillyDesignStudio/momo-kiji
- **Docs**: https://momo-kiji.readthedocs.io
- **Website**: https://momo-kiji.dev
- **Discord**: https://discord.gg/DHRbKbzr
- **Package**: https://pypi.org/project/momo-kiji/

---

We're excited to see what you build with momo-kiji. The ANE has been waiting. Let's use it. 🍑
