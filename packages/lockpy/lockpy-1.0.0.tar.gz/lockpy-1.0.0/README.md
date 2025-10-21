# 🐍 lockpy — Access Control for Python

`lockpy` brings **powerful, enforced access control patterns** to Python — something you normally only get in languages like **Java** or **C#**.

It provides decorators like:
- `@singleton` — ensures only one instance of a class exists.  
- `@private` — prevents external access to methods (enforced at runtime).  
- I'm currently working on modifiers like : `@protected`, `@final`, `@readonly` - will include in other releases

---

## 🚀 Features

- `Lightweight`: no dependencies required  
- `Inspired from static typed languaged`: private/protected/final behavior  
- `Runtime Enforcement`: enfore rules at runtime (no special interpreter required)  
- `Flexible`: works with instance methods, classmethods, and staticmethods  

---

## 📦 Installation

```pip command
pip install lockpy
