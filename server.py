from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yonetici-gizli-anahtar'
socketio = SocketIO(app, cors_allowed_origins="*")

active_users = {}

# --- YÖNETİCİ GİRİŞİ VE ODA ŞİFRESİ ---
print("\n" + "="*40)
print("   🔒 YÖNETİCİ ŞİFRELEME PANELİ 🔒")
print("="*40)

try:
    print("Öneri P: 2147483647 (Büyük bir asal sayı)")
    ADMIN_P = int(input("Sistem için Asal Sayı (P) girin: "))
    
    print("Öneri G: 2, 5 veya 7")
    ADMIN_G = int(input("Sistem için Taban Sayı (G) girin: "))
except ValueError:
    print("❌ Hatalı giriş! Varsayılan değerler atanıyor (P:2147483647, G:7)")
    ADMIN_P = 2147483647
    ADMIN_G = 7

# YENİ: Yöneticinin belirlediği odaya giriş şifresi
ADMIN_PASSWORD = input("\n🔑 Odaya giriş için bir GİZLİ ŞİFRE belirleyin: ")

print(f"\n✅ Şifreleme Parametreleri ve Oda Şifresi Belirlendi!")
print(f"📡 Sistem yayına hazır. P:{ADMIN_P}, G:{ADMIN_G}\n")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('adminParameters', {'p': ADMIN_P, 'g': ADMIN_G})

@socketio.on('join')
def on_join(data):
    user_id = data['user_id']
    pub_key = data['public_key']
    entered_password = data.get('room_password', '')
    
    # YENİ: Şifre Kontrol Mekanizması
    if entered_password != ADMIN_PASSWORD:
        print(f"⚠️ {user_id} hatalı şifre denedi!")
        emit('joinError', {'message': '❌ Hatalı oda şifresi! Giriş reddedildi.'})
        return

    # Şifre doğruysa normal işlemlere devam et
    active_users[user_id] = {"public_key": pub_key, "sid": request.sid}
    join_room(user_id)
    join_room('genel_grup')
    print(f"🟢 {user_id} odaya girdi. DH Açık Anahtarı: {pub_key}")
    
    # İstemciye (tarayıcıya) girişin başarılı olduğunu bildir
    emit('joinSuccess', {'user_id': user_id})
    
    clean_keys = {u: active_users[u]['public_key'] for u in active_users}
    emit('updateUserList', clean_keys, to='genel_grup')

@socketio.on('sendMessage')
def handle_send_message(data):
    emit('messageStatus', {'status': 'sent', 'messageId': data['messageId']}, to=data['senderId'])
    emit('receiveMessage', data, to='genel_grup', include_self=False)

@socketio.on('messageDelivered')
def handle_delivered(data):
    emit('updateStatus', {'status': 'delivered', 'messageId': data['messageId'], 'reader': data['reader']}, to=data['senderId'])

@socketio.on('messageRead')
def handle_read(data):
    emit('updateStatus', {'status': 'read', 'messageId': data['messageId'], 'reader': data['reader']}, to=data['senderId'])

@socketio.on('disconnect')
def on_disconnect():
    disconnected_user = None
    for user_id, info in list(active_users.items()):
        if info['sid'] == request.sid:
            disconnected_user = user_id
            del active_users[user_id]
            break
    if disconnected_user:
        clean_keys = {u: active_users[u]['public_key'] for u in active_users}
        emit('updateUserList', clean_keys, to='genel_grup')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002, debug=False)
    
