# ColorGradText

**ColorGradText** is a Python module that allows you to apply amazing color gradients to text and ASCII art in your terminal.  
It supports **horizontal and vertical gradients**, works with multi-line text, and comes with **10 creative gradient presets**.

![](https://github.com/OgTen/GradientText/blob/main/images/aqua_wave.png)
![](https://github.com/OgTen/GradientText/blob/main/images/rose_blush.png)
![](https://github.com/OgTen/GradientText/blob/main/images/violet_dream.png)
![](https://github.com/OgTen/GradientText/blob/main/images/sunflare.png)
![](https://github.com/OgTen/GradientText/blob/main/images/frostbite.png)
![](https://github.com/OgTen/GradientText/blob/main/images/ember_glow.png)
![](https://github.com/OgTen/GradientText/blob/main/images/tidepool.png)
![](https://github.com/OgTen/GradientText/blob/main/images/evenfall.png)
![](https://github.com/OgTen/GradientText/blob/main/images/lime_light.png)
![](https://github.com/OgTen/GradientText/blob/main/images/dreamcloud.png)
![](https://github.com/OgTen/GradientText/blob/main/images/gradtexts.png)

```
from colorgradtext import aqua_wave

text = "Og_Ten"
print(aqua_wave(text))
```
```
from colorgradtext import lime_light

ascii = r"""
   ____   _____            _______ ______ _   _ 
  / __ \ / ____|          |__   __|  ____| \ | |
 | |  | | |  __              | |  | |__  |  \| |
 | |  | | | |_ |             | |  |  __| | . ` |
 | |__| | |__| |             | |  | |____| |\  |
  \____/ \_____|   _______   |_|  |______|_| \_|                        
                  |_______|   
"""

print(lime_light(ascii, direction="vertical"))
```

**Download: ``pip install colorgradtext``**
