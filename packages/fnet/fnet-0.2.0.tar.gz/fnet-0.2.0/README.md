# fnet_0.2.0
„fnet_0.2.0 — еволюция на FractalNet“

🐛 История на версиите
v0.1.0
Първоначална версия с базова архитектура и един фрактален генератор

v0.1.1
Премахната зависимост от turtle

Подобрена съвместимост и стабилност

v0.1.3
Добавени 7 фрактални генератора

Въведени Dataset-и за всяка фрактална форма

Създаден ReducedFractalDataset

Завършен __init__.py с __all__

Подготвена за PyPI

✅ v0.2.0 (текуща)
Преименуване на проекта: FractalNet → fnet_0.2.0

Подобрена структура на импортиране

Добавен Jupyter бележник с демонстрации (fnet_0_2_0.ipynb)

Подготвена за бъдещо разширение с нови модели и фрактали

📚 Лиценз
MIT License — свободна за използване, модификация и разпространение.

🌐 Репозитори
🔗 GitHub: AlexKitipov/fnet_0.2.0

# fnet_0.2.0 — Еволюция на FractalNet

## 🧠 Концепция

`fnet_0.2.0` е модулна PyTorch библиотека, вдъхновена от фракталната геометрия. Тя комбинира фрактални генератори, PyTorch Dataset класове и невронна архитектура, базирана на рекурсивни блокове. Подходяща е за обучение върху изображения, сигнали и абстрактни структури.

---

## ⚙️ Основни характеристики

- **Фрактални генератори**: Koch, Sierpinski, L-System, Dragon Curve, Mandelbrot, Julia, Lindenmayer
- **PyTorch Dataset-и**: За всяка фрактална форма + обединен `ReducedFractalDataset`
- **FractalNet архитектура**: Рекурсивна невронна мрежа с регулируема дълбочина
- **Модулна структура**: Разделени модули `ml/`, `fractals/`, `datasets/`
- **Готова за разширяване**: Лесно добавяне на нови фрактали или модели

git clone https://github.com/AlexKitipov/fnet_0.2.0.git
cd fnet_0.2.0
pip install -e .

📦 Импортиране и използване

from FractalNet.ml.fractal_layers import FractalNet as FractalNetModel
from FractalNet.fractals.koch import KochDataset
from FractalNet.fractals.sierpinski import SierpinskiDataset
from FractalNet.fractals.l_system import LSystemDataset
from FractalNet.fractals.dragon import DragonDataset
from FractalNet.fractals.mandelbrot import MandelbrotDataset
from FractalNet.fractals.julia import JuliaDataset
from FractalNet.fractals.lindenmayer import LindenmayerDataset
from FractalNet.datasets.reduced import ReducedFractalDataset


🧪 Пример

model = FractalNetModel()
dataset = KochDataset(num_samples=10)

print(model)
print(f"Брой изображения: {len(dataset)}")


---

## 🚀 Инсталация

```bash
pip install fnet_0.2.0
