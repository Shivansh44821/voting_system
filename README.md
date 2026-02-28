# 🗳️ Student Voting System using Streamlit & MySQL

A simple and intuitive web-based voting system for educational institutions, built using **Streamlit** and **MySQL**. This project enables students to cast votes securely and provides an admin interface to manage elections and view results with visual insights.

## 📌 Features

- 🔐 **Student Login with Password Protection**
- ✅ **One Vote Per Student**
- 📊 **Real-Time Voting Result Display**
- 📈 **Interactive Charts using Altair or Plotly**
- 🧑‍💼 **Admin Portal**  
  - Add/Delete Candidates  
  - View Vote Counts  
  - Reset Election Data

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/)  
- **Backend:** [MySQL](https://www.mysql.com/)  
- **Database Connector:** `mysql-connector-python`  
- **Visualization:** Altair / Plotly  
- **Others:** `pandas`

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Shivansh44821/voting_system.git
cd voting_system
````

### 2. Install Dependencies
```bash
pip install streamlit mysql-connector-python pandas altair plotly
```

### 3. Set Up MySQL Database

* Open MySQL Workbench or any client
* Create a database named:

```sql
CREATE DATABASE voting_system;
```
### 4. Update DB Credentials

In `online_voting_system.py`, update:

```python
db = mysql.connector.connect(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="voting_system"
)
```

### 5. Run the Streamlit App

```bash
streamlit run online_voting_system.py
```

---

## 📚 Use Cases

* College/School Student Elections
* Internal Organizational Voting
* Department-Level Polls

---

## 🤝 Contributing

Contributions, issues and feature requests are welcome!
Feel free to open a [Pull Request](https://github.com/Shivansh44821/voting_system/pulls).

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

Shivansh Srivastava
[GitHub Profile](https://github.com/Shivansh44821)
Prashant Saini
[GitHub Profile](https://github.com/prashant-GKV)
UTKARSH GUPTA 
[GitHub Profile]
.(https://github.com/Utkarsh-Gupta-Git-Hub)


