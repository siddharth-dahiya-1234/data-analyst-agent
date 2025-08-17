
# 🌟 **TDS Project 2: Data Analyst Agent**

> **A smart, interactive, and beautiful way to analyze your data — powered by Google Generative AI & cutting-edge Python tools.**
> **Repo:** [📂 View on GitHub](https://github.com/23f1000805/tds-project-2)

---

## 📌 **Overview**

The **TDS Data Analyst Agent** transforms raw data into **actionable insights** in minutes.
Upload your dataset + questions, and get:

* 📊 **Interactive Visualizations**
* 🧠 **AI-Driven Insights**
* ⚡ **Automated Analysis Workflows**

Perfect for **business analysts, researchers, and data enthusiasts** who want **fast, accurate, and beautiful results** without manual crunching.

---

## ✨ **Features at a Glance**

| Feature                     | Description                                        |
| --------------------------- | -------------------------------------------------- |
| 🔍 **Intelligent Analysis** | Understands your data using Google's Generative AI |
| 📈 **Dynamic Charts**       | Visualizes data with Matplotlib & Seaborn          |
| 🌐 **Web Scraping**         | Pulls data from URLs in seconds                    |
| 📁 **Multi-Format Support** | Works with CSV, Excel, JSON, Parquet, TXT          |
| 🔄 **Batch Processing**     | Answers multiple questions in one go               |
| 🎨 **Modern UI**            | Clean, responsive, and beginner-friendly           |
| ⚡ **Real-Time Results**     | Progress tracking with fast computations           |

---
## 👤 **Author & Credits**

Developed by **[Siddharth](https://www.linkedin.com/in/siddharth-dahiya-496a622a2/)**

---
## 🚀 **Quick Start for more detail read `DEPLOYMENT_GUIDE.md` **

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/23f2003642/data-analyst-agent.git
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3️⃣ Set Environment Variables**

Create a `.env` file:

### **4️⃣ Run the App**

```bash
python -m uvicorn app:app --reload
```

Then open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 📖 **How to Use**

### **Step 1: Select Question from test_question file:**


### **Step 2: Upload Required DataSet for your question if any**

* **Required:** Questions file (`.txt`)
* **Optional:** Dataset in CSV/Excel/JSON/Parquet/TXT

### **Step 3: Get Your Insights**

* 🧮 **Processed by AI**
* 📊 **Visualized beautifully**
* 💡 **Actionable recommendations generated**

---

## 🛠 **Tech Stack**

**Backend**

* FastAPI 🚀 (Ultra-fast web framework)
* LangChain 🧠 (LLM orchestration)
* Google Generative AI ✨ (Smart insights)
* Pandas + NumPy 📊 (Data manipulation)
* Matplotlib + Seaborn 🎨 (Visualizations)

---

## 🔧 **API Endpoints**

| Method | Endpoint   | Description                |
| ------ | ---------- | -------------------------- |
| `GET`  | `/`        | Main web interface         |
| `POST` | `/api` | Process questions + data   |

---

## 📂 **Supported Data Formats**

| Format  | Extensions      |
| ------- | --------------- |
| CSV     | `.csv`          |
| JSON    | `.json`         |
| Parquet | `.parquet`      |
| Text    | `.txt`          |

---

## 🎯 **Use Cases**

* **Business Intelligence** – Sales trends, customer insights
* **Research** – Statistical summaries, hypothesis testing
* **Data Science** – EDA, feature analysis, anomaly detection

---

## 🔒 **Security**

* Local data processing (no cloud storage)
* Environment variable protection for API keys
* Configurable CORS for production environments

---

## 🚀 **Deployment Options**

* **Local** → `python -m uvicorn app:app --reload`
* **Production** → `code in entrypoint.sh`

## 🤝 **Contributing**

We welcome PRs!

1. Fork the repo
2. Create a branch: `git checkout -b feature-name`
3. Commit + push
4. Submit PR 🚀

---

## 📜 **License**

Licensed under **MIT** — Free to use, modify, and share.

---
