const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// YENİ: Eski mesajları aklımızda tutacağımız liste
const mesajGecmisi = [];

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
  console.log('Yeni bir kullanıcı bağlandı!');

  // YENİ: Kullanıcı odaya girdiği anda, aklımızdaki geçmişi sadece ona gönder
  socket.emit('gecmisi yukle', mesajGecmisi);

  socket.on('chat message', (msg) => {
    // YENİ: Gelen yeni mesajı geçmiş listemize ekle
    mesajGecmisi.push(msg);
    
    // YENİ: Sunucunun belleği dolmasın diye sadece son 50 mesajı tutalım
    if (mesajGecmisi.length > 50) {
      mesajGecmisi.shift(); // En eski olan 1. mesajı siler
    }

    io.emit('chat message', msg);
  });

  socket.on('typing', (isim) => {
    socket.broadcast.emit('typing', isim);
  });

  socket.on('disconnect', () => {
    console.log('Bir kullanıcı ayrıldı.');
  });
});

server.listen(3000, () => {
  console.log('Sunucu çalışıyor! Tarayıcıda şu adrese gidin: http://localhost:3000');
});
