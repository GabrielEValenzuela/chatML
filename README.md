# chatML 🤖  

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)   ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-4ea94b?style=for-the-badge&logo=mongodb&logoColor=white)  

---

## 🧐 Overview  

**chatML** is a powerful API designed for working with **Knowledge Graphs (KGs)** using **PyKeen** and **FastAPI**. It provides scalable and efficient ways to perform **entity similarity searches, relationship predictions, and graph-based reasoning**. The project leverages machine learning models like **TransH** to enhance knowledge inference capabilities.

💡 **What is a Knowledge Graph?**  
A **Knowledge Graph** represents information as a set of entities and their relationships, enabling structured reasoning, semantic search, and intelligent recommendations.  

🚀 **Why chatML?**  
- FastAPI-based high-performance API  
- Integration with **PyKeen** for Knowledge Graph Embeddings  
- Scalable data storage with PostgreSQL & MongoDB  
- Efficient caching using Redis  
- **Docker-ready** for seamless deployment  

---

## ✨ Features  

✔️ **Knowledge Graph Embedding** – Supports models like **TransH**, **TransE**, and **RotatE**  
✔️ **Entity Similarity** – Retrieve semantically similar entities  
✔️ **Relationship Prediction** – Predict missing links in the graph  
✔️ **Graph Querying API** – Intuitive endpoints to interact with the KG  
✔️ **Rate Limiting** – Protects API from excessive usage (Freemium vs Premium)  
✔️ **Authentication & API Keys** – Secure access to endpoints  
✔️ **Docker Support** – Easy deployment with containerized services  

---

## 🛠 Technologies Used  

- 🐍 **Python 3.x**  
- ⚡ **FastAPI** (for high-performance web services)  
- 🧠 **PyKeen** (for Knowledge Graph Embeddings)  
- 🐘 **PostgreSQL** (for structured storage)  
- 🍃 **MongoDB** (for flexible document storage)  
- 🔥 **Redis** (for caching)  
- 🐳 **Docker** (for containerization)  

---

## 🚀 Installation and Setup  

### 🔧 Local Setup  

1️⃣ **Clone the repository**  

```bash
git clone https://github.com/GabrielEValenzuela/chatML
cd chatML
```

2️⃣ **Install dependencies**  

```bash
pip install -r requirements.txt
```

3️⃣ **Set up environment variables**  

Create a `.env` file in the root directory with:  

```plaintext
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=api_db
POSTGRES_USER=api_user
POSTGRES_PASSWORD=api_password
MONGO_URI=mongodb://localhost:27017
MONGO_DB=api_user_db
REDIS_HOST=localhost
REDIS_PORT=6379
```

4️⃣ **Run the application**  

```bash
uvicorn src.api.main:app --reload
```

📌 The API will be accessible at: **`http://localhost:8000`**  

---

### 🐳 Running with Docker  

1️⃣ **Build the Docker image**  

```bash
docker build -t chatml-api .
```

2️⃣ **Run the Docker container**  

```bash
docker run -d -p 8000:8000 --env-file .env chatml-api
```

📌 The API will be available at: **`http://localhost:8000`**  

---

## 📡 API Usage  

💡 **Example: Get Similar Entities**  

**Endpoint:**  
```http
POST /service
```

**Request:**
```http
{
  "api_key": <API_KEY>,
  "entity_input": "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site3_50561744"
}
```

```http
{
  "api_key": <API_KEY>,
  "entity_input": 106110
}
```

**Response:**  
```json
{
    "cache": true,
    "result": [
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1552552768",
            -14.311209678649902
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1377663274",
            -14.149274826049805
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1563165924",
            -14.016729354858398
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1537220480",
            -13.844208717346191
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site1_14574103",
            -13.730814933776855
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1623902330",
            -13.727827072143555
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1483671550",
            -13.700096130371094
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site3_50138121",
            -13.663334846496582
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1390531503",
            -13.654467582702637
        ],
        [
            "https://raw.githubusercontent.com/jwackito/csv2pronto/main/ontology/pronto.owl#space_site2_A1362021113",
            -13.56968879699707
        ]
    ]
}
```

More endpoints and documentation can be found in the **Home endpoint** 📖  

---

## 📖 Knowledge Graphs & More  

For a deeper understanding of **Knowledge Graphs**, **PyKeen**, and model training, check out our [Wiki](wiki-url).  

🔬 **Topics covered in the Wiki:**  
✅ What are Knowledge Graphs?  
✅ How PyKeen works?  
✅ Training custom embedding models  
✅ API endpoint documentation  

---

## 📜 License  

This project is licensed under the **GNU General Public License (GPL)**.  

---

🌟 **Contributions & Feedback**  

Feel free to **fork, contribute, or submit issues** to help improve this project! 🚀  
