import tkinter as tk
from tkinter import simpledialog
import socketio
import time

# Socket istemcisi
sio = socketio.Client()

my_id = ""
target_id = ""

# --- ARAYÜZ (GUI) FONKSİYONLARI ---

def append_message(msg, color="black"):
    """Ekrana mesaj ve durum yazdırmak için yardımcı fonksiyon"""
    chat_window.config(state='normal')
    chat_window.insert(tk.END, msg + '\n', color)
    chat_window.tag_config(color, foreground=color)
    chat_window.config(state='disabled')
    chat_window.yview(tk.END) # Otomatik en alta kaydır

def send_message(event=None):
    """Gönder butonuna veya Enter'a basıldığında çalışır"""
    msg = msg_entry.get()
    if msg:
        append_message(f"[Sen]: {msg}", "black") # Kendi mesajımızı ekrana yaz
        msg_entry.delete(0, tk.END) # Kutuyu temizle
        
        # Sunucuya gidecek paket (Daha sonra AES eklenecek)
        mesaj_paketi = {
            'messageId': f'msg_{int(time.time())}',
            'senderId': my_id,
            'recipientId': target_id,
            'encryptedContent': f'[ŞİFRELİ] {msg}'
        }
        sio.emit('sendMessage', mesaj_paketi)

# --- SUNUCUDAN GELEN OLAYLAR ---

@sio.event
def connect():
    append_message("🟢 Sunucuya bağlanıldı!", "green")
    sio.emit('join', {'user_id': my_id})

@sio.on('messageStatus')
def on_message_status(data):
    append_message("  ✔️ (Tek Tık) Sunucuya ulaştı", "gray")

@sio.on('updateStatus')
def on_update_status(data):
    if data['status'] == 'delivered':
        append_message("  ✔️✔️ (Çift Tık) Karşı cihaza iletildi", "gray")
    elif data['status'] == 'read':
        append_message("  🔵🔵 (Mavi Tık) Karşı taraf okudu!", "blue")

@sio.on('receiveMessage')
def on_receive_message(data):
    append_message(f"\n[{data['senderId']}]: {data['encryptedContent']}", "purple")
    
    # 1. Aşama: Mesaj telefona düştü (Çift Tık bildirimi at)
    sio.emit('messageDelivered', {'messageId': data['messageId'], 'senderId': data['senderId']})
    
    # 2. Aşama: 2 saniye sonra okundu simülasyonu (Mavi tık bildirimi at)
    # root.after, arayüzü dondurmadan süre saymamızı sağlar
    root.after(2000, lambda: sio.emit('messageRead', {'messageId': data['messageId'], 'senderId': data['senderId']}))


# --- ANA PENCERE TASARIMI ---

root = tk.Tk()
root.geometry("420x550")
root.configure(bg="#e5ddd5") # Whatsapp arkaplan rengine benzer bir ton

# Uygulama açıldığında kullanıcı bilgilerini sor
root.withdraw() # Ana pencereyi popup çıkana kadar gizle
my_id = simpledialog.askstring("Giriş Yap", "Kullanıcı Adınız (Örn: A):", parent=root)
target_id = simpledialog.askstring("Sohbet", "Kiminle Mesajlaşacaksınız? (Örn: B):", parent=root)
root.deiconify() # Ana pencereyi geri getir
root.title(f"Şifreli Sohbet: {my_id} -> {target_id}")

# Sohbet Ekranı (Mesajların aktığı yer)
chat_window = tk.Text(root, state='disabled', bg="white", font=("Helvetica", 11), wrap=tk.WORD)
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Alt kısım: Mesaj yazma yeri ve Gönder butonu
input_frame = tk.Frame(root, bg="#e5ddd5")
input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

msg_entry = tk.Entry(input_frame, font=("Helvetica", 12))
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=5)
msg_entry.bind("<Return>", send_message) # Enter tuşuna basınca gönder

send_btn = tk.Button(input_frame, text="GÖNDER", command=send_message, bg="#075e54", fg="white", font=("Helvetica", 10, "bold"))
send_btn.pack(side=tk.RIGHT, ipady=3, ipadx=10)

# Sunucuya bağlan ve arayüzü başlat
try:
    sio.connect('http://localhost:5000')
except:
    append_message("HATA: Sunucuya bağlanılamadı! server.py açık mı?", "red")

# Pencereyi açık tutan döngü
root.mainloop()
