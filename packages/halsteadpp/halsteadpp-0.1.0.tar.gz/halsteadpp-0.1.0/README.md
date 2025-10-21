# 🧮 Halstead++

**Halstead++** is a lightweight static analysis tool for **C source code**, built in Python.  
It leverages **Abstract Syntax Tree (AST)** parsing to compute both **Halstead complexity metrics** and **Cyclomatic complexity**, providing structured insights into code readability, logical structure, and cognitive effort.

This tool offers a clear, visually rich output directly in the terminal — ideal for developers, educators, and researchers studying code complexity or program structure.

---

## ✨ Key Features

- 📊 **Halstead Metrics**
  - Distinct operators (n₁), distinct operands (n₂)  
  - Total operators (N₁), total operands (N₂)  
  - Vocabulary, Length, Volume, Difficulty, Effort, Time, Estimated Bugs  

- 🔁 **Cyclomatic Complexity (McCabe)** per function  

- 🌳 **AST-based analysis** using [`pycparser`](https://github.com/eliben/pycparser)  

- 🎨 **Beautiful console output** with [`rich`](https://github.com/Textualize/rich)  

- ⚙️ **Preprocessing support** for handling macros and standard headers (`gcc -E`)  

- 🧩 Modular design — can be used both as a **CLI tool** or **Python module**

---

## 📦 Installation

### From PyPI
```
pip install halsteadpp
```

### From GitHub
```
pip install git+https://github.com/Morgadineo/Halsteadpp.git
```

## 🚀 Usage

