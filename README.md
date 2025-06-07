# 🎥 Frame Interpolation App

A Streamlit-based app that lets you compare **naive pixel-averaging** vs. a **deep U-Net** model (with VGG16 perceptual loss) for video frame interpolation. Upload your video, crank up the frame rate, and see the results side-by-side!

![App Preview](./media/preview.png)  
### Try it yourself here: 

---

## ⚡ Results

| Original |  Deep U-Net Interpolation |
|:--------:|:-------------------------:|
| ![Original](./media/preinterpolate1.mp4) | ![Deep](./media/interpolated1.mp4.mp4) |
| ![Original](./media/preinterpolate2.mp4) | ![Deep](./media/interpolated2.mp4) |

---

## 🏗️ Architecture

- **Model**: Custom U-Net encoder–decoder  
- **Losses**:  
  - L1 pixel loss  
  - VGG16-based perceptual (feature) loss  
- **Training**:  
  - Vimeo90K triplets, 512×512 crops  
  - Adam optimizer, 50 epochs, Cosine LR schedule  

---

## 🛠️ Installation & Running

1. Clone the repo  
   ```bash
   git clone https://github.com/kkakdugee/frame-interpolation.git
   cd frame-interpolation
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ``` 

3. Run
   ```bash
   streamlit run app.py
   ```