import socketio
import time

# İstemci (Client) oluştur
sio = socketio.Client()

# Kullanıcı bilgilerini al
my_id = input("Kullanıcı adınız (Örn: A): ")
target_id = input("Mesaj atacağınız kişi (Örn: B): ")

# --- SUNUCUDAN GELENLERİ DİNLEME ---

@sio.event
def connect():
    print(f"🟢 Sunucuya bağlanıldı! Odanız: {my_id}")
    # Bağlanınca sunucuya adımızı söylüyoruz ki bizi odamıza alsın
    sio.emit('join', {'user_id': my_id})

@sio.on('messageStatus')
def on_message_status(data):
    print(f"✔️ [TEK TIK] Mesaj sunucuya ulaştı.") 

@sio.on('updateStatus')
def on_update_status(data):
    if data['status'] == 'delivered':
        print(f"✔️✔️ [ÇİFT TIK] Mesaj karşı tarafın cihazına indi.")
    elif data['status'] == 'read':
        print(f"🔵🔵 [MAVİ TIK] Mesaj karşı tarafça OKUNDU!")

@sio.on('receiveMessage')
def on_receive_message(data):
    print(f"\n📩 YENİ MESAJ GELDİ: {data['encryptedContent']}")
    
    # 1. Aşama: Mesaj telefona düştü (Otomatik Çift Tık bildirimi atıyoruz)
    time.sleep(1) # Gerçekçi olması için 1 saniye bekle
    sio.emit('messageDelivered', {'messageId': data['messageId'], 'senderId': data['senderId']})
    
    # 2. Aşama: Kullanıcı mesajı okudu (Mavi Tık bildirimi atıyoruz)
    time.sleep(2) # 2 saniye sonra okumuş gibi yap
    print("👀 Mesaja bakıldı. Okundu bilgisi gönderiliyor...")
    sio.emit('messageRead', {'messageId': data['messageId'], 'senderId': data['senderId']})

# --- BAĞLANTI VE MESAJ GÖNDERME ---

if __name__ == '__main__':
    # Sunucuya bağlan
    sio.connect('http://localhost:5000')
    
    print("\n--- SOHBET BAŞLADI ---")
    while True:
        # Kullanıcıdan mesaj al
        mesaj = input("\nGönder (Çıkmak için 'q'): ")
        if mesaj.lower() == 'q':
            break
            
        # Gönderilecek paketi hazırla
        mesaj_paketi = {
            'messageId': f'msg_{int(time.time())}', # Benzersiz bir ID uydur
            'senderId': my_id,
            'recipientId': target_id,
            'encryptedContent': f'[ŞİFRELİ METİN] {mesaj}' # Normalde burada AES olacak
        }
        
        # Sunucuya fırlat
        sio.emit('sendMessage', mesaj_paketi)

    sio.disconnect()
    