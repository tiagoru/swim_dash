# swim_dash

# 🏊‍♂️ Olympic Swimming Split Times Dashboard


## 🌟 Overview
This **Dash-powered web application** analyzes **Olympic swimming split times**, allowing users to:
- 📈 **Visualize pacing trends** for different heats
- 🔥 **Analyze split time heatmaps**
- 🏅 **Compare total times per swimmer**
- 🔄 **Use Dynamic Time Warping (DTW) to compare performance trends**

🚀 **Live Demo:** [Your Render App URL](https://your-app-url.onrender.com)  
📊 **Built With:** `Dash`, `Plotly`, `Pandas`, `NumPy`, `Gunicorn`, `dtaidistance`

---

## 📂 Folder Structure

swim-dash │── app.py # Main Dash application │── df_swim_paris.csv # Dataset for analysis │── requirements.txt # Python dependencies │── runtime.txt # Specifies Python version │── Procfile # Heroku/Render deployment file │── README.md # Project documentation

python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

pip install -r requirements.txt

python app.py
