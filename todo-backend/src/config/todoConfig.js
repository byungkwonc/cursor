const mongoose = require('mongoose');

// MongoDB 연결
const connectDB = async () => {
    try {
        const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/todo-app';

        const options = {
            useNewUrlParser: true,	// URL 파서 사용
            useUnifiedTopology: true,	// 통합 토폴로지 엔진 사용
            autoIndex: true,	// 자동 인덱스 생성
            serverSelectionTimeoutMS: 5000, // 서버 선택 타임아웃
            socketTimeoutMS: 45000, // 소켓 타임아웃
            family: 4 // IPv4 사용
        };

        await mongoose.connect(mongoURI, options);

        mongoose.connection.on('connected', () => {
            console.log('MongoDB 연결 성공');
        });

        mongoose.connection.on('error', (err) => {
            console.error('MongoDB 연결 에러:', err);
        });

        mongoose.connection.on('disconnected', () => {
            console.log('MongoDB 연결이 끊어졌습니다. 재연결 시도 중...');
        });

        // 애플리케이션 종료 시 DB 연결 종료
        process.on('SIGINT', async () => {
            await mongoose.connection.close();
            console.log('MongoDB 연결이 종료되었습니다.');
            process.exit(0);
        });

    } catch (error) {
        console.error('MongoDB 초기 연결 실패:', error);
        process.exit(1);
    }
};

module.exports = connectDB;