from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 允许前端跨域访问


# 获取数据库文件的绝对路径
def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'contacts.db')


# 初始化数据库
def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  email TEXT,
                  address TEXT)''')
    conn.commit()
    conn.close()
    print(f"数据库初始化完成，路径: {db_path}")


# 获取数据库连接
def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    return conn


# 获取所有联系人
@app.route('/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM contacts")
        contacts = [{'id': row[0], 'name': row[1], 'phone': row[2], 'email': row[3], 'address': row[4]} for row in
                    c.fetchall()]
        conn.close()
        return jsonify(contacts)
    except Exception as e:
        return jsonify({'error': f'获取联系人失败: {str(e)}'}), 500


# 添加联系人
@app.route('/contacts', methods=['POST'])
def add_contact():
    try:
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email', '')
        address = data.get('address', '')

        if not name or not phone:
            return jsonify({'error': '姓名和电话是必填项'}), 400

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                  (name, phone, email, address))
        conn.commit()
        contact_id = c.lastrowid
        conn.close()

        return jsonify({'id': contact_id, 'name': name, 'phone': phone, 'email': email, 'address': address}), 201
    except Exception as e:
        return jsonify({'error': f'添加联系人失败: {str(e)}'}), 500


# 修改联系人
@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    try:
        data = request.get_json()
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email', '')
        address = data.get('address', '')

        if not name or not phone:
            return jsonify({'error': '姓名和电话是必填项'}), 400

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE contacts SET name=?, phone=?, email=?, address=? WHERE id=?",
                  (name, phone, email, address, contact_id))

        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': '联系人不存在'}), 404

        conn.commit()
        conn.close()

        return jsonify({'id': contact_id, 'name': name, 'phone': phone, 'email': email, 'address': address})
    except Exception as e:
        return jsonify({'error': f'更新联系人失败: {str(e)}'}), 500


# 删除联系人
@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM contacts WHERE id=?", (contact_id,))

        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': '联系人不存在'}), 404

        conn.commit()
        conn.close()

        return jsonify({'message': '联系人删除成功'})
    except Exception as e:
        return jsonify({'error': f'删除联系人失败: {str(e)}'}), 500


# 健康检查端点
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Contacts API is running'})


if __name__ == '__main__':
    init_db()
    # 生产环境配置
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
