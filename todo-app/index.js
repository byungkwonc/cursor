const express = require('express');
const path = require('path');
const app = express();
const PORT = 9090;

// 정적 파일 제공
app.use(express.static(path.join(__dirname, 'src')));
app.use(express.json());

// HTML 파일 제공
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'src', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Frontend server is running on http://localhost:${PORT}`);
});