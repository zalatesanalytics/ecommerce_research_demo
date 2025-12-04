\# Ecommerce Search Analytics \& Relevance Tuning Demo



This repo is a \*\*self-contained demo\*\* designed to show how I would support

Account Executives and engineers at an ecommerce search company (e.g. Constructor)

with data-driven insights, dashboards, and A/B test thinking.



\## 🔍 What this project demonstrates



\- Turning raw \*\*search log data\*\* into KPIs and insights  

\- Identifying \*\*high-volume, low-CTR queries\*\* as optimization opportunities  

\- Suggesting \*\*relevance tuning actions\*\* (synonyms, boosts, ranking tweaks)  

\- Running a simple \*\*A/B simulation\*\* to estimate business impact  

\- Communicating findings in a way that supports \*\*pre-sales demos\*\* and \*\*product teams\*\*



\## 📂 Structure



\- `generate\_data.py` – creates a synthetic but realistic `ecommerce\_search\_logs.csv`

\- `ecommerce\_search\_logs.csv` – sample dataset (generated)

\- `app.py` – Streamlit app for interactive exploration \& A/B simulation

\- `analysis.ipynb` – exploratory data analysis and experiment ideas

\- `requirements.txt` – Python dependencies



\## ▶️ How to run



```bash

\# 1. Create dataset

python generate\_data.py



\# 2. Install dependencies

pip install -r requirements.txt



\# 3. Launch Streamlit app

streamlit run app.py



