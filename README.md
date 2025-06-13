# OCR
A basic OCR (Optical Character Recognition) project using DFT (Discrete Fourier Transform).

## 📄 Overview
This project demonstrates how to implement a simple OCR system using frequency domain techniques. While it isn't production-ready, it serves as a learning tool for understanding the mechanics behind OCR.

## 📁 Directory Structure

- **Fonts supported:** `arial` (sans-serif) and `rockwell` (serif)
- **Character patterns:**  
  `/utils/characters/{fontname}/`
- **Test images:**  
  `/utils/tests/{fontname}/`
- **Recognition results:**  
  `/utils/results/{fontname}/`
- **Character locations (from last run):**  
  `/utils/found_locations/`
- **Usage examples:**  
  `/examples/`

## 🚀 How to Use

See example usage in:  
`/examples/ex1.py`

Modify the font and test image name as needed:
```python
font = "rockwell"
name = "Mt5"
main(f"utils/tests/{font}/{name}.png", font, ["lower", "special", "polish"], 0)
```

## Conclusion
<ins>This OCR is **not** by any means perfect, it only shows how one can be implemented. For acurracy use _pytesseract_ or other libraries.</ins>

With that being said I am pretty happy with the results! Within the output text I can "see" the image that was tested, furthermore my friends without being shown images (though they are pretty well known) managed to decipher them and guess the source. 

Unfortunately this OCR is very rotation-sensitive and can parse somewhat well images that are only rotated by $\lessapprox 0.5\degree$, others will be unreadable.