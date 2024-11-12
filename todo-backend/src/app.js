const express = require('express');
const cors = require('cors');
const connectDB = require('./config/todoConfig');
const todoRoutes = require('./routes/todoRoute');
require('dotenv').config();

const app = express();

// 데이터베이스 연결
connectDB();

// 미들웨어 설정
app.use(cors());
app.use(express.json());

// 라우트 설정
app.use('/api/todos', todoRoutes);

// 에러 핸들링
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        success: false,
        message: '서버 에러가 발생했습니다.',
        error: process.env.NODE_ENV === 'development' ? err.message : {}
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`서버가 ${PORT}번 포트에서 실행 중입니다.`);
});