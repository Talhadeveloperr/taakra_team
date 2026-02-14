require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const sql = require('mssql');
const cookieParser = require('cookie-parser');
const cors = require('cors');
const http = require('http'); 
const { Server } = require('socket.io'); 

const authRoutes = require('./routes/auth');

const app = express();
const server = http.createServer(app); 

// Middleware
app.use(express.json());
app.use(cookieParser());
app.use(
  cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  })
);

// --- Socket.io Configuration ---
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
    methods: ["GET", "POST"]
  }
});

// --- SQL Server Configuration (Kept for your other routes) ---
const sqlConfig = {
    user: 'admin',
    password: 'admin1234',
    server: '10.9.53.147',
    database: 'taakra_db', 
    port: 1433,
    options: {
        encrypt: false,
        trustServerCertificate: true,
    },
    pool: { max: 10, min: 0, idleTimeoutMillis: 30000 }
};

// --- WebSocket Logic (Volatile/Live-Only) ---
io.on('connection', (socket) => {
  console.log(`📡 New Socket Connection: ${socket.id}`);

  socket.on('join_room', (roomId) => {
    socket.join(roomId);
    console.log(`👥 User ${socket.id} joined room: ${roomId}`);
  });

  // Handle incoming messages - DB Logic Removed
  socket.on('send_message', (data) => {
    const { roomId, user_id, full_name, message, university } = data;

    // Relay the message instantly to everyone in the room
    io.to(roomId).emit('receive_message', {
      user_id,
      full_name,
      message,
      university,
      timestamp: new Date()
    });

    console.log(`💬 Message relayed from ${full_name} in room ${roomId}`);
  });

  socket.on('disconnect', () => {
    console.log('🔌 User disconnected');
  });
});

// --- Unified Connection Function ---
const startServer = async () => {
  try {
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/auth-system');
    console.log('✅ MongoDB connected');

    const pool = await sql.connect(sqlConfig);
    console.log("✅ Successfully connected to taakra_db!");
    app.locals.sqlPool = pool; 

    const PORT = process.env.PORT || 5000;
    server.listen(PORT, () => {
      console.log(`🚀 Server & WebSockets running on http://localhost:${PORT}`);
    });

  } catch (err) {
    console.error('❌ Startup Error:', err.message);
    process.exit(1);
  }
};

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/categories', require('./routes/category'));
app.use('/api/competitions', require('./routes/competetion'));
app.use('/api/competetion-registrations', require('./routes/competetionregistrations'));
app.use('/api/adminanalytics', require('./routes/analyticsroute'));

app.get('/health', (req, res) => {
  res.status(200).json({ success: true, message: 'Server is running and DBs are active' });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ success: false, message: 'Internal server error' });
});

startServer();