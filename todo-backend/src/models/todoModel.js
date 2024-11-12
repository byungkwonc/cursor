const mongoose = require('mongoose');

// Mongoose 스키마 정의
const todoSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    trim: true
  },
  content: {
    type: String,
    trim: true
  },
  completed: {
    type: Boolean,
    default: false
  },
  dueDate: {
    type: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  order: {
    type: Number,
    default: 0
  }
});

// 모델 생성 및 사용
module.exports = mongoose.model('Todo', todoSchema);