from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问


# 初始化数据库
def init_db():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  email TEXT,
                  address TEXT)''')
    conn.commit()
    conn.close()


# 获取所有联系人
@app.route('/contacts', methods=['GET'])
def get_contacts():
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM contacts")
    contacts = [{'id': row[0], 'name': row[1], 'phone': row[2], 'email': row[3], 'address': row[4]} for row in
                c.fetchall()]
    conn.close()
    return jsonify(contacts)


# 添加联系人
@app.route('/contacts', methods=['POST'])
def add_contact():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email', '')
    address = data.get('address', '')

    if not name or not phone:
        return jsonify({'error': '姓名和电话是必填项'}), 400

    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
              (name, phone, email, address))
    conn.commit()
    contact_id = c.lastrowid
    conn.close()

    return jsonify({'id': contact_id, 'name': name, 'phone': phone, 'email': email, 'address': address}), 201


# 修改联系人
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email', '')
    address = data.get('address', '')

    if not name or not phone:
        return jsonify({'error': '姓名和电话是必填项'}), 400

    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?",
              (name, phone, email, address, contact_id))
    conn.commit()
    conn.close()

    return jsonify({'id': contact_id, 'name': name, 'phone': phone, 'email': email, 'address': address})


# 删除联系人
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    conn = sqlite3.connect('contacts.db')
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': '联系人删除成功'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)