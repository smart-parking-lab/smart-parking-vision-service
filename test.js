const mqtt = require('mqtt');
require('dotenv').config();

// Khởi tạo kết nối với Broker
const client = mqtt.connect(process.env.MQTT_BROKER, {
    clientId: (process.env.MQTT_CLIENT_ID || 'be1_lpr') + '_test', 
    port: parseInt(process.env.MQTT_PORT, 10)
});

client.on('error', (err) => {
    console.error('❌ Lỗi kết nối MQTT:', err);
});

client.on('connect', () => {
    console.log('✅ BE1 (LPR) đã kết nối MQTT thành công.');
    // Đăng ký nhận tín hiệu từ cảm biến vật cản tại cổng (Entry/Exit)
    client.subscribe('sensors/gate/+', { qos: 1 });
});

client.on('message', (topic, message) => {
    try {
        console.log(`📩 Nhận tín hiệu từ topic: ${topic}`);
        
        // GIẢ LẬP: Sau khi thuật toán AI nhận diện xong biển số
        const result = { 
            plate: "79A-12345", 
            gate: topic.split('/').pop(), // Lấy 'entry' hoặc 'exit' từ topic
            timestamp: new Date().toISOString()
        };

        // Gửi kết quả biển số sang cho BE2 xử lý logic
        client.publish('payment_status', JSON.stringify(result), { qos: 1 });
        console.log('📤 Đã gửi thông tin biển số sang BE2.');
    } catch (err) {
        console.error('❌ Lỗi xử lý tin nhắn tại BE1:', err.message);
    }
});